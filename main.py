import yfinance as yf # For Stock Data
import feedparser # For News (RSS)
import os
from bs4 import BeautifulSoup

proxy_url = "http://127.0.0.1:7897"

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
        for ticker in self.stocks:
            data = yf.Ticker(ticker)
            company_name = data.info.get('shortName', ticker)
            print(f"{company_name} {ticker}: ${data.fast_info.last_price:.2f}")

# 2. THE NEWS (HK & US)
    def get_news_pulse(self):

        print("\n--- TOP NEWS HEADLINES ---")
        for category, url in self.news_feeds.items():
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]: # Only top 3 stories
                print(f"[{category}] {entry.title}")

#3. Run
    def run(self):
        self.get_market_pulse()
        self.get_news_pulse()

if __name__ == "__main__":
    dashboard = PersonalDashboard()
    dashboard.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
