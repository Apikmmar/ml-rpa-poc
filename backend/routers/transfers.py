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
    if from_location == to_location and from_rack == to_rack:
        raise HTTPException(400, "Source and destination location/rack cannot be the same")
    if quantity < 1:
        raise HTTPException(400, "Quantity must be at least 1")
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
        available = stock_fields.get("available", 0)
        if quantity > available:
            raise HTTPException(400, f"Insufficient stock for '{sku}': requested {quantity}, available {available}")
        stock_id = stock_data["records"][0]["id"]
        now = datetime.utcnow().isoformat()
        auto_approve = quantity <= 30
        status = "Completed" if auto_approve else "Pending"
        payload = {
            "fields": {
                "from_location": from_location, 
                "to_location": to_location, 
                "from_rack": from_rack, 
                "to_rack": to_rack, 
                "sku": sku, 
                "quantity": quantity, 
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
        if auto_approve:
            await client.patch(f"{BASE_URL}/Stocks/{stock_id}", headers=HEADERS, json={
                "fields": {"location": to_location, "rack": to_rack, "updated_at": now, "updated_by": requested_by}
            })
        return {
            "transfer_id": transfer_id,
            "status": status,
            "stock_updated": auto_approve
        }

@router.patch("/{transfer_id}/approve")
async def approve_transfer(transfer_id: str, approved_by: str = "Ops"):
    async with httpx.AsyncClient() as client:
        tr_resp = await client.get(f"{BASE_URL}/Stock_Transfers/{transfer_id}", headers=HEADERS)
        if tr_resp.status_code != 200:
            raise HTTPException(404, "Transfer not found")
        tr_fields = tr_resp.json().get("fields", {})
        if tr_fields.get("status") != "Pending":
            raise HTTPException(400, f"Transfer is already {tr_fields.get('status')}")
        sku = tr_fields["sku"]
        to_location = tr_fields["to_location"]
        to_rack = tr_fields["to_rack"]
        stocks = await client.get(f"{BASE_URL}/Stocks?filterByFormula={{sku}}='{sku}'", headers=HEADERS)
        stock_data = stocks.json()
        if not stock_data.get("records"):
            raise HTTPException(404, f"SKU '{sku}' not found")
        stock_id = stock_data["records"][0]["id"]
        available = stock_data["records"][0]["fields"].get("available", 0)
        quantity = tr_fields["quantity"]
        if quantity > available:
            raise HTTPException(400, f"Insufficient stock for '{sku}' at approval time: requested {quantity}, available {available}")
        now = datetime.utcnow().isoformat()
        await client.patch(f"{BASE_URL}/Stock_Transfers/{transfer_id}", headers=HEADERS, json={
            "fields": {"status": "Completed", "approved_by": approved_by, "updated_at": now, "updated_by": approved_by}
        })
        await client.patch(f"{BASE_URL}/Stocks/{stock_id}", headers=HEADERS, json={
            "fields": {"location": to_location, "rack": to_rack, "updated_at": now, "updated_by": approved_by}
        })
        return {"transfer_id": transfer_id, "status": "Completed", "stock_updated": True}

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
