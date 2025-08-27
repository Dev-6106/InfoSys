from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

from db import SessionLocal, Product
from scrapers.example_shop import ExampleShopScraper

def update_prices():
    """Fetch latest prices for all products and update DB."""
    db: Session = SessionLocal()
    try:
        products = db.query(Product).all()
        scraper = ExampleShopScraper()
        for p in products:
            try:
                data = scraper.fetch_product_data(p.url)
                p.price = data.get("price")
                p.last_checked = datetime.now()
                db.add(p)
                db.commit()
                logger.info(f"Updated {p.name}: {p.price}")
            except Exception as e:
                logger.exception(f"Failed updating {p.url}: {e}")
                db.rollback()
    finally:
        db.close()

def seed_from_csv(csv_path: str = "data/samples/seed_products.csv"):
    import pandas as pd
    db: Session = SessionLocal()
    try:
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            exists = db.query(Product).filter(Product.url == row["url"]).first()
            if not exists:
                db.add(Product(name=row["name"], url=row["url"]))
        db.commit()
    finally:
        db.close()
