from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from db import SessionLocal, init_db, Product
from schemas import ProductCreate, Product as ProductSchema
from services.aggregator import update_prices

app = FastAPI(title="Competitor Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_prices, "interval", minutes=10, id="price_updater", replace_existing=True)
    scheduler.start()
    app.state.scheduler = scheduler

@app.on_event("shutdown")
def on_shutdown():
    sched = getattr(app.state, "scheduler", None)
    if sched:
        sched.shutdown(wait=False)

@app.post("/products/", response_model=ProductSchema)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.url == product.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists for this URL")
    db_product = Product(name=product.name, url=product.url)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=list[ProductSchema])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
