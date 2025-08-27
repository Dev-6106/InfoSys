# NOTE: This is a demo scraper; adjust selectors for real targets.
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper

class ExampleShopScraper(BaseScraper):
    def fetch_product_data(self, url: str) -> dict:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # Demo selectors; replace with real ones.
        name_tag = soup.find("h1") or soup.title
        price_tag = soup.find(class_="price") or soup.find(id="price")
        name = name_tag.get_text(strip=True) if name_tag else "Unknown Product"
        price_text = price_tag.get_text(strip=True) if price_tag else "0"
        # crude USD $123.45 -> 123.45
        price = float(''.join(ch for ch in price_text if ch.isdigit() or ch=='.') or 0)
        return {"name": name, "price": price}
