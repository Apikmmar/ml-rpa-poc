from fastapi import APIRouter, HTTPException, Query
import httpx
from datetime import datetime
from config import BASE_URL, HEADERS

router = APIRouter(prefix="/stocks", tags=["stocks"])

_stocks_cache = {"data": None, "cached_at": None}
CACHE_TTL = 86400

SORT_PARAMS = "?sort[0][field]=created_at&sort[0][direction]=desc"

async def _fetch_stocks():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Stocks{SORT_PARAMS}", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        _stocks_cache["data"] = resp.json()
        _stocks_cache["cached_at"] = datetime.utcnow().timestamp()
        return _stocks_cache["data"]

@router.get("")
async def list_stocks(refresh: bool = Query(False)):
    now_ts = datetime.utcnow().timestamp()
    cache_stale = (
        _stocks_cache["data"] is None or
        _stocks_cache["cached_at"] is None or
        (now_ts - _stocks_cache["cached_at"]) > CACHE_TTL
    )
    if refresh or cache_stale:
        return await _fetch_stocks()
    return _stocks_cache["data"]

@router.post("/goods-receipt")
async def receive_goods(sku: str, quantity: int, location: str, rack: str, received_by: str = "System"):
    async with httpx.AsyncClient() as client:
        stocks = await client.get(f"{BASE_URL}/Stocks?filterByFormula={{sku}}='{sku}'", headers=HEADERS)
        stock_data = stocks.json()
        if stock_data["records"]:
            stock_record = stock_data["records"][0]
            stock_id = stock_record["id"]
            stock_fields = stock_record["fields"]
            registered_location = stock_fields.get("location")
            registered_rack = stock_fields.get("rack")
            if registered_location and registered_location != location:
                raise HTTPException(400, f"SKU '{sku}' is registered at {registered_location}, not {location}")
            if registered_rack and registered_rack != rack:
                raise HTTPException(400, f"SKU '{sku}' is registered at {registered_rack}, not {rack}")
            now = datetime.utcnow().isoformat()
            
            receipt_payload = {
                "fields": {
                    "link_sku": [stock_id], 
                    "quantity": quantity, 
                    "location": location, 
                    "rack": rack, 
                    "received_by": received_by, 
                    "status": "Completed", 
                    "created_at": now, 
                    "created_by": received_by, 
                    "updated_at": now, 
                    "updated_by": received_by
                }
            }
            
            receipt_resp = await client.post(f"{BASE_URL}/Good_Receipts", headers=HEADERS, json=receipt_payload)
            
            if receipt_resp.status_code != 200:
                raise HTTPException(status_code=receipt_resp.status_code, detail=receipt_resp.text)
            
            current_add = stock_fields.get("add_stock", 0)
            stock_payload = {
                "fields": {
                    "add_stock": current_add + quantity, 
                    "updated_at": now, 
                    "updated_by": received_by
                }
            }
            
            await client.patch(f"{BASE_URL}/Stocks/{stock_id}", headers=HEADERS, json=stock_payload)
            
            return {
                "receipt_id": receipt_resp.json().get("id"), 
                "status": "received", "sku": sku, 
                "quantity": quantity, 
                "location": location, 
                "rack": rack
            }
    raise HTTPException(404, "SKU not found")

@router.get("/goods-receipts")
async def list_goods_receipts():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Good_Receipts{SORT_PARAMS}", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()
