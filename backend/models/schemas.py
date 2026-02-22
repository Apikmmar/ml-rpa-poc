from pydantic import BaseModel
from typing import List

class OrderItem(BaseModel):
    sku: str
    qty: int

class CreateOrderRequest(BaseModel):
    customer_email: str
    customer_id: str
    priority: str = "Normal"
    items: List[OrderItem]

class UpdateStatusRequest(BaseModel):
    status: str
    eta: str | None = None
