import yfinance as yf # For Stock Data
import feedparser # For News (RSS)
import os
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
        self.stocks = ["TSLA", "AAPL", "NVDA", "0700.HK", "2800.HK"]  # Add your portfolio here
        self.news_feeds = {
            "Global Business": "https://search.cnbc.com/rs/search/view.xml?partnerId=2000&keywords=business",
            "HK News (SCMP)": "https://www.scmp.com/rss/2/feed",
            "World": "https://qz.com/feed",
            "Tech": "https://www.theverge.com/rss/index.xml"
        }

# 1. THE STOCKS (NBA and Markets)
    def get_market_pulse(self):
        print("--- MARKET UPDATES ---")

        # 1. Fetch ALL tickers at once (One single request instead of five)
        tickers_obj = yf.Tickers(" ".join(self.stocks), session=session)

        for ticker in self.stocks:
            try:
                # 2. Access the data from the pre-fetched object
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

            except Exception as e:
                print(f"Could not fetch {ticker}: {e}")


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


