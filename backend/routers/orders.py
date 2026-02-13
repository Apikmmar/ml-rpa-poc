from fastapi import APIRouter, HTTPException
import httpx
from datetime import datetime
from config import BASE_URL, HEADERS
from models.schemas import CreateOrderRequest, UpdateStatusRequest

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("")
async def create_order(order: CreateOrderRequest):
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()
        payload = {"fields": {"customer_email": order.customer_email, "customer_id": order.customer_id, "priority": order.priority, "status": "Pending", "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
        resp = await client.post(f"{BASE_URL}/Orders", headers=HEADERS, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        
        order_id = resp.json()["id"]
        
        for item in order.items:
            stocks = await client.get(f"{BASE_URL}/Stocks?filterByFormula={{sku}}='{item.sku}'", headers=HEADERS)
            stock_data = stocks.json()
            if stock_data["records"]:
                stock_id = stock_data["records"][0]["id"]
                item_payload = {"fields": {"order_id": [order_id], "sku": [stock_id], "qty": item.qty, "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
                await client.post(f"{BASE_URL}/Order_Items", headers=HEADERS, json=item_payload)
        
        return {"order_id": order_id, "automation": "Order Validator triggered"}

@router.get("")
async def list_orders():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Orders", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@router.get("/{order_id}")
async def get_order(order_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@router.patch("/{order_id}/status")
async def update_order_status(order_id: str, req: UpdateStatusRequest):
    async with httpx.AsyncClient() as client:
        payload = {"fields": {"status": req.status}}
        resp = await client.patch(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return {"order_id": order_id, "status": req.status}
