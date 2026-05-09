import time
import fetch_news

def run():
    while True:
        print("🔄 Updating data...")
        fetch_news.fetch_news_rss(["TSLA", "AAPL", "GOOGL"])
        print("⏳ Sleeping 1 min...\n")        
        time.sleep(300)

if __name__ == "__main__":
    run()
