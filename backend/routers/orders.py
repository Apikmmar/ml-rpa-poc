from fastapi import APIRouter, HTTPException, Query
import httpx
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
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

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), retry=retry_if_exception_type(httpx.HTTPStatusError))
async def patch_airtable(client: httpx.AsyncClient, url: str, payload: dict):
    resp = await client.patch(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp

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

@router.post("/{order_id}/reserve")
async def reserve_stock(order_id: str):
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()

        items_resp = await client.get(f"{BASE_URL}/Order_Items?filterByFormula={{order_id}}='{order_id}'", headers=HEADERS)
        items = items_resp.json().get("records", [])
        if not items:
            raise HTTPException(404, "No order items found")

        reserved, shortages = [], []
        for item in items:
            f = item["fields"]
            qty_needed = f.get("qty", 0)
            avb_qty = f.get("avb_qty", 0)
            sku = f.get("item_sku") or f.get("lookup_sku", "")

            if avb_qty >= qty_needed:
                reserved.append({"sku": sku, "qty": qty_needed})
            else:
                if avb_qty > 0:
                    reserved.append({"sku": sku, "qty": avb_qty})
                shortages.append({"sku": sku, "qty_needed": qty_needed, "qty_available": avb_qty})

        if shortages:
            for shortage in shortages:
                backorder_payload = {"fields": {"original_order_id": [order_id], "items": str(shortage), "status": "Pending", "qty_needed": shortage["qty_needed"], "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
                await client.post(f"{BASE_URL}/Backorders", headers=HEADERS, json=backorder_payload)

        status = "Reserved" if not shortages else ("Failed" if not reserved else "Reserved")
        try:
            await patch_airtable(client, f"{BASE_URL}/Orders/{order_id}", {"fields": {"status": status, "updated_at": now, "updated_by": "System"}})
        except Exception:
            raise HTTPException(503, "Failed to update order status after 3 retries")

        return {
            "order_id": order_id, 
            "reserved": reserved, 
            "shortages": shortages, 
            "status": status
        }
