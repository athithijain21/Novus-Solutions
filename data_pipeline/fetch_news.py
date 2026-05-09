import asyncio
import requests
import xml.etree.ElementTree as ET
from playwright.async_api import async_playwright

def fetch_news_rss(ticker):
    try:
        url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
        response = requests.get(url, timeout=5)
        root = ET.fromstring(response.content)
        return [item.find('title').text for item in root.findall('./channel/item')[:5]]
    except:
        return []

async def fetch_news_playwright(ticker):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f"https://www.google.com/finance/quote/{ticker}:NASDAQ", timeout=20000)
            selectors = ['.tY7f9e', '.Yf6CWc', 'div[role="heading"]']
            headlines = []
            for s in selectors:
                found = await page.locator(s).all_inner_texts()
                headlines.extend([h for h in found if len(h) > 25])
            await browser.close()
            return list(set(headlines))[:5]
    except:
        return []

def get_all_news(ticker):
    """Orchestrates the fallback logic"""
    news = fetch_news_rss(ticker)
    if not news:
        news = asyncio.run(fetch_news_playwright(ticker))
    return news