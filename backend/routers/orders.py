from fastapi import APIRouter, HTTPException, Query
import httpx
from datetime import datetime
from config import BASE_URL, HEADERS
from models.schemas import CreateOrderRequest, UpdateStatusRequest

router = APIRouter(prefix="/orders", tags=["orders"])

_orders_cache = {"data": None, "cached_at": None}
CACHE_TTL = 86400

async def _fetch_orders():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Orders", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        _orders_cache["data"] = resp.json()
        _orders_cache["cached_at"] = datetime.utcnow().timestamp()
        return _orders_cache["data"]

@router.post("")
async def create_order(order: CreateOrderRequest):
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()
        payload = {
            "fields": {
                "customer_email": order.customer_email, 
                "customer_id": order.customer_id, 
                "priority": order.priority, 
                "status": "Pending", 
                "created_at": now, 
                "created_by": "System", 
                "updated_at": now, 
                "updated_by": "System"
                }
            }
        resp = await client.post(f"{BASE_URL}/Orders", headers=HEADERS, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        
        order_id = resp.json()["id"]
        
        for item in order.items:
            stocks = await client.get(f"{BASE_URL}/Stocks?filterByFormula={{sku}}='{item.sku}'", headers=HEADERS)
            stock_data = stocks.json()
            if stock_data["records"]:
                stock_id = stock_data["records"][0]["id"]
                item_payload = {
                    "fields": {
                        "order_id": [order_id], 
                        "sku": [stock_id], 
                        "qty": item.qty, 
                        "created_at": now, 
                        "created_by": "System", 
                        "updated_at": now, 
                        "updated_by": "System"
                        }
                    }
                await client.post(f"{BASE_URL}/Order_Items", headers=HEADERS, json=item_payload)
        
        _orders_cache["data"] = None  # invalidate cache
        return {
            "order_id": order_id, 
            "automation": "Order Validator triggered"
        }

@router.get("")
async def list_orders(refresh: bool = Query(False)):
    now_ts = datetime.utcnow().timestamp()
    cache_stale = (
        _orders_cache["data"] is None or
        _orders_cache["cached_at"] is None or
        (now_ts - _orders_cache["cached_at"]) > CACHE_TTL
    )
    if refresh or cache_stale:
        return await _fetch_orders()
    return _orders_cache["data"]

@router.patch("/{order_id}/status")
async def update_order_status(order_id: str, req: UpdateStatusRequest):
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()
        fields = {
            "status": req.status, 
            "updated_at": now, 
            "updated_by": "System"
        }
        if req.eta:
            fields["eta"] = req.eta
        resp = await client.patch(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS, json={"fields": fields})
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return {
            "order_id": order_id, 
            "status": req.status, 
            "eta": req.eta
        }