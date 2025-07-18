from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DetectionResponse(BaseModel):
    vegetable: str
    quantity: float
    confidence: float


class DetectionRequest(BaseModel):
    location: str = "Delhi"


class ContributionRequest(BaseModel):
    vegetable: str
    price: float
    location: str
    user_code: str


class PriceData(BaseModel):
    price: float
    unit: str = "kg"
    location: str
    last_updated: datetime


class VegetableInfo(BaseModel):
    name: str
    display_name: str
    category: str
    seasonal: bool = False
