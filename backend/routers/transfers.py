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
async def create_stock_transfer(from_location: str, to_location: str, from_rack: str, to_rack: str, sku: str, quantity: int, requested_by: str):
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()
        payload = {
            "fields": {
                "from_location": from_location, 
                "to_location": to_location, 
                "from_rack": from_rack, 
                "to_rack": to_rack, 
                "sku": sku, 
                "quantity": quantity, 
                "status": "Pending", 
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
        return {
            "transfer_id": resp.json()["id"], 
            "automation": "Transfer Approval triggered"
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
