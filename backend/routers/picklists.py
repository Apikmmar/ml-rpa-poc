from fastapi import APIRouter, HTTPException, Query
import httpx
from datetime import datetime
from config import BASE_URL, HEADERS
from models.schemas import UpdateStatusRequest

router = APIRouter(prefix="/picklists", tags=["picklists"])

_picklists_cache = {"data": None, "cached_at": None}
CACHE_TTL = 86400

async def _fetch_picklists():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Picklists", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        _picklists_cache["data"] = resp.json()
        _picklists_cache["cached_at"] = datetime.utcnow().timestamp()
        return _picklists_cache["data"]

@router.get("")
async def list_picklists(refresh: bool = Query(False)):
    now_ts = datetime.utcnow().timestamp()
    cache_stale = (
        _picklists_cache["data"] is None or
        _picklists_cache["cached_at"] is None or
        (now_ts - _picklists_cache["cached_at"]) > CACHE_TTL
    )
    if refresh or cache_stale:
        return await _fetch_picklists()
    return _picklists_cache["data"]

@router.patch("/{picklist_id}/status")
async def update_picklist_status(picklist_id: str, req: UpdateStatusRequest):
    async with httpx.AsyncClient() as client:
        payload = {"fields": {"status": req.status}}
        resp = await client.patch(f"{BASE_URL}/Picklists/{picklist_id}", headers=HEADERS, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return {
            "picklist_id": picklist_id, 
            "status": req.status
        }

@router.get("/{picklist_id}/route")
async def optimize_route(picklist_id: str):
    async with httpx.AsyncClient() as client:
        pl_resp = await client.get(f"{BASE_URL}/Picklists/{picklist_id}", headers=HEADERS)
        if pl_resp.status_code != 200:
            raise HTTPException(status_code=pl_resp.status_code, detail=pl_resp.text)
        pl_fields = pl_resp.json().get("fields", {})
        order_ids = pl_fields.get("order_id", [])
        if not order_ids:
            raise HTTPException(404, "No order linked to this picklist")

        order_id = order_ids[0]
        items_resp = await client.get(
            f"{BASE_URL}/Order_Items?filterByFormula={{order_id}}='{order_id}'", headers=HEADERS
        )
        items = items_resp.json().get("records", [])
        if not items:
            raise HTTPException(404, "No order items found")

        stops = []
        for item in items:
            f = item["fields"]
            sku_ids = f.get("sku", [])
            if not sku_ids:
                continue
            stock_resp = await client.get(f"{BASE_URL}/Stocks/{sku_ids[0]}", headers=HEADERS)
            if stock_resp.status_code != 200:
                continue
            sf = stock_resp.json().get("fields", {})
            stops.append({
                "sku": f.get("item_sku") or f.get("lookup_sku", ""),
                "qty": f.get("qty", 0),
                "location": sf.get("location", ""),
                "rack": sf.get("rack", ""),
                "stop": f"{sf.get('location', '')}/{sf.get('rack', '')}"
            })

        stops.sort(key=lambda x: (x["location"], x["rack"]))
        return {
            "picklist_id": picklist_id,
            "order_id": order_id,
            "optimized_route": stops
        }

