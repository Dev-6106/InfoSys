from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def fetch_product_data(self, url: str) -> dict:
        """Return a dict with at least { 'name': str, 'price': float }"""
        raise NotImplementedError
