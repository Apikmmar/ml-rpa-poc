from fastapi import APIRouter, HTTPException, Query
import httpx
from datetime import datetime
from config import BASE_URL, HEADERS

router = APIRouter(prefix="/stock-transfers", tags=["transfers"])

_transfers_cache = {"data": None, "cached_at": None}
CACHE_TTL = 86400

async def _fetch_transfers():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Stock_Transfers", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        _transfers_cache["data"] = resp.json()
        _transfers_cache["cached_at"] = datetime.utcnow().timestamp()
        return _transfers_cache["data"]

@router.post("")
async def create_stock_transfer(from_location: str, to_location: str, from_rack: str, to_rack: str, sku: str, requested_by: str):
    if from_location == to_location and from_rack == to_rack:
        raise HTTPException(400, "Source and destination location/rack cannot be the same")
    async with httpx.AsyncClient() as client:
        stocks = await client.get(f"{BASE_URL}/Stocks?filterByFormula={{sku}}='{sku}'", headers=HEADERS)
        stock_data = stocks.json()
        if not stock_data.get("records"):
            raise HTTPException(404, f"SKU '{sku}' not found in inventory")
        stock_fields = stock_data["records"][0]["fields"]
        registered_location = stock_fields.get("location")
        registered_rack = stock_fields.get("rack")
        if registered_location and registered_location != from_location:
            raise HTTPException(400, f"SKU '{sku}' is registered at {registered_location}, not {from_location}")
        if registered_rack and registered_rack != from_rack:
            raise HTTPException(400, f"SKU '{sku}' is registered at {registered_rack}, not {from_rack}")
        stock_id = stock_data["records"][0]["id"]
        now = datetime.utcnow().isoformat()
        status = "Completed"
        payload = {
            "fields": {
                "from_location": from_location, 
                "to_location": to_location, 
                "from_rack": from_rack, 
                "to_rack": to_rack, 
                "sku": sku, 
                "status": status, 
                "requested_by": requested_by, 
                "created_at": now, 
                "created_by": requested_by, 
                "updated_at": now, 
                "updated_by": requested_by
            }
        }
        resp = await client.post(f"{BASE_URL}/Stock_Transfers", headers=HEADERS, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        transfer_id = resp.json()["id"]
        await client.patch(f"{BASE_URL}/Stocks/{stock_id}", headers=HEADERS, json={
            "fields": {"location": to_location, "rack": to_rack, "updated_at": now, "updated_by": requested_by}
        })
        return {
            "transfer_id": transfer_id,
            "status": status,
            "stock_updated": True
        }

@router.get("")
async def list_stock_transfers(refresh: bool = Query(False)):
    now_ts = datetime.utcnow().timestamp()
    cache_stale = (
        _transfers_cache["data"] is None or
        _transfers_cache["cached_at"] is None or
        (now_ts - _transfers_cache["cached_at"]) > CACHE_TTL
    )
    if refresh or cache_stale:
        return await _fetch_transfers()
    return _transfers_cache["data"]
