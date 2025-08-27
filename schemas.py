from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    name: str
    url: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    price: Optional[float] = None
    last_checked: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
