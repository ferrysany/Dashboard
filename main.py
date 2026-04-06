import yfinance as yf # For Stock Data
import feedparser # For News (RSS)
import os, csv
import platform
import requests
from bs4 import BeautifulSoup
from curl_cffi.requests import Session as BrowserSession
import socket

def is_proxy_working(host="127.0.0.1", port=7897, timeout=2):
    """Checks if your local VPN port is actually open."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError):
        return False


# --- 1. Environment & Session Setup ---
IS_WINDOWS = platform.system() == "Windows"
# Streamlit Cloud sets this environment variable automatically
IS_STREAMLIT = os.getenv('STREAMLIT_RUNTIME_ENV') is not None

# Create a "Browser-like" session
# 'impersonate="chrome"' is the key to bypassing Yahoo's bot detection
session = BrowserSession(impersonate="chrome")

if IS_WINDOWS and is_proxy_working():
    # Use your local VPN proxy
    session.proxies = {
        "http": "http://127.0.0.1:7897",
        "https": "http://127.0.0.1:7897"
    }
    print("🚀 Proxy Active: Using VPN.")
    print("🚀 Windows Mode: VPN + Browser Impersonation Active")
else:
    # No proxy needed in the cloud
    session.proxies = {}
    print("🌐 Proxy Inactive: Using Direct Connection.")
    print("☁️ Cloud Mode: Direct Browser Impersonation Active")

# Ensure the session ignores system-wide proxy settings
session.trust_env = False

#proxy_url = "http://127.0.0.1:7897"

#os.environ['HTTP_PROXY'] = proxy_url
#os.environ['HTTPS_PROXY'] = proxy_url
#os.environ['http_proxy'] = proxy_url
#os.environ['https_proxy'] = proxy_url

class PersonalDashboard:

    def __init__(self):
        #self.stocks = ["TSLA", "AAPL", "NVDA", "0700.HK", "2800.HK"]  # Add your portfolio here
        self.stocks = self._load_stocks_from_csv()
        self.news_feeds = {
            "Global Business": "https://search.cnbc.com/rs/search/view.xml?partnerId=2000&keywords=business",
            "HK News (SCMP)": "https://www.scmp.com/rss/2/feed",
            "World": "https://qz.com/feed",
            "Tech": "https://www.theverge.com/rss/index.xml"
        }
# 1. THE STOCKS
    def _load_stocks_from_csv(self):
        if os.path.exists('stocks.csv'):
            with open('stocks.csv', 'r') as f:
                reader = csv.reader(f)
                return [row['symbol'] for row in reader]
        return ["TSLA", "AAPL", "NVDA", "0700.HK", "2800.HK"]

# 2. GET STOCKS PRICE FROM AASTOCKS
    def fetch_aastocks(self, symbol):
        if ".HK" in symbol:
            url = f"http://www.aastocks.com/en/mobile/quote.aspx?symbol={symbol.replace('.HK', '').zfill(5)}"
        elif any(x in symbol for x in [".SS", ".SZ"]):
            url = f"http://www.aastocks.com/en/cnhk/quote/quote.aspx?symbol={symbol.split('.')[0]}"
        else:
            url = f"http://www.aastocks.com/en/usq/quote/quote.aspx?symbol={symbol}"
        print(f"DEBUG: Fetching {url}")

        try:
            resp = session.get(url, timeout=10)

            html_text = resp.text
            soup = BeautifulSoup(html_text, 'html.parser')

            price_tag = soup.find("div", class_="quote_last") or soup.find("span", class_=["pos", "neg", "unc"])
            #change_tag = soup.find(class_="quote_chg_per")

            price = price_tag.get('data-value') if price_tag and price_tag.has_attr('data-value') else None

            if not price and price_tag:
                price = price_tag.text.strip()

            if not price:
                import re
                # This regex looks for a number after the word "last" or "price" in the JS code
                match = re.search(r'last["\']\s*:\s*["\']([\d\.,]+)["\']', html_text)
                if match:
                    price = match.group(1)
            #if price_tag and change_tag:
            #    return f"**{symbol}**: {price_tag.text.strip()} ({change_tag.text.strip()}) [AA]"
            #return f"**{symbol}**: Symbol not found on AASTOCKS"

            #if not price_tag:
                # Find any tag containing "Closed" and get the next sibling text
            #    closed_label = soup.find(lambda tag: tag.name == "span" and "Closed" in tag.text)
            #    if closed_label:
                    # Often the price is in the parent div or a span next to it
            #        price_tag = closed_label.find_next(class_="pos") or closed_label.find_next(class_="neg")

            #if price_tag:
            #    p = price_tag.text.strip()
                # Clean up the change text if it exists
                #c = change_tag.text.strip() if change_tag else "0.00%"
            #    return f"**{symbol}**: {p}) [AA] Price is available"

            if price:
                return f"**{symbol}**: {price} ) [AA]"

            return f"**{symbol}**: Data Locked (JS Required)"

        except Exception as e:
            return f"**{symbol}**: {e}"

# 2. GET THE STOCKS PRICE (Markets)
    def get_market_pulse(self):
        print("--- MARKET UPDATES ---")

        # 1. Fetch ALL tickers at once (One single request instead of one by one)
        tickers_obj = yf.Tickers(" ".join(self.stocks), session=session)

        for ticker in self.stocks:
            try:
                # 2. GET QUOTE FROM AASTOCKS
                print(self.fetch_aastocks(ticker))
            except:
                print(f"**{symbol}**: Fetch Error")
                # 2. FALL BACK TO YAHOO
                data = tickers_obj.tickers[ticker]

                # Try to get info safely
                # NOTE: Use .fast_info for price to avoid heavy API calls
                current_price = data.fast_info.last_price
                open_price = data.fast_info.open

                # Calculate the difference
                change_amount = current_price - open_price
                percent_change = (change_amount/open_price)*100

                company_name = data.info.get('shortName', ticker)

                # Determine display sign
                sign = "+" if change_amount >= 0 else ""

                print(f"{company_name} {ticker}: ${current_price:.2f}"
                      f"({sign}{percent_change:.2f}%)")

# 2. THE NEWS (HK & US)
    def get_news_pulse(self):

        print("\n--- TOP NEWS HEADLINES ---")
        for category, url in self.news_feeds.items():
            response = session.get(url)
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:3]: # Only top 3 stories
                full_title = entry.get('title', 'No title').strip()
                full_title = " ".join(full_title.split())

                print(f"[{category}] {full_title}")

#3. Run
    def run(self):
        self.get_market_pulse()
        self.get_news_pulse()

if __name__ == "__main__":
    dashboard = PersonalDashboard()
    dashboard.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/




