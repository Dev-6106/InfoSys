from urllib.parse import urlparse
from .example_shop import ExampleShopScraper

_REGISTRY = {
    # Map hostname to scraper class
    "example.com": ExampleShopScraper,
}

def get_scraper_for(url: str):
    host = urlparse(url).hostname or ""
    # pick exact or fallback
    cls = _REGISTRY.get(host, ExampleShopScraper)
    return cls()
