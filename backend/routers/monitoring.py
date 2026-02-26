from fastapi import APIRouter, HTTPException, Query
import httpx
import asyncio
from datetime import datetime
from config import BASE_URL, HEADERS

router = APIRouter(tags=["monitoring"])

CACHE_TTL = 86400
_cache = {
    "exceptions":    {"data": None, "cached_at": None},
    "audit_logs":    {"data": None, "cached_at": None},
    "backorders":    {"data": None, "cached_at": None},
    "notifications": {"data": None, "cached_at": None},
    "metrics":       {"data": None, "cached_at": None},
}

def _is_stale(key):
    c = _cache[key]
    return c["data"] is None or c["cached_at"] is None or (datetime.utcnow().timestamp() - c["cached_at"]) > CACHE_TTL

def _set(key, data):
    _cache[key]["data"] = data
    _cache[key]["cached_at"] = datetime.utcnow().timestamp()
    return data

SORT_PARAMS = "?sort[0][field]=created_at&sort[0][direction]=desc"

@router.get("/exceptions")
async def list_exceptions(refresh: bool = Query(False)):
    if not refresh and not _is_stale("exceptions"):
        return _cache["exceptions"]["data"]
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Exceptions{SORT_PARAMS}", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return _set("exceptions", resp.json())

@router.get("/audit-logs")
async def list_audit_logs(refresh: bool = Query(False)):
    if not refresh and not _is_stale("audit_logs"):
        return _cache["audit_logs"]["data"]
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/AuditLogs{SORT_PARAMS}", headers=HEADERS)
async def list_backorders(refresh: bool = Query(False)):
    if not refresh and not _is_stale("backorders"):
        return _cache["backorders"]["data"]
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Backorders{SORT_PARAMS}", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return _set("backorders", resp.json())

@router.get("/notifications")
async def list_notifications(refresh: bool = Query(False)):
    if not refresh and not _is_stale("notifications"):
        return _cache["notifications"]["data"]
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Notifications{SORT_PARAMS}", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return _set("notifications", resp.json())

@router.get("/metrics/dashboard")
async def get_metrics(refresh: bool = Query(False)):
    if not refresh and not _is_stale("metrics"):
        return _cache["metrics"]["data"]
    async with httpx.AsyncClient() as client:
        orders_resp, logs_resp = await asyncio.gather(
            client.get(f"{BASE_URL}/Orders", headers=HEADERS),
            client.get(f"{BASE_URL}/AuditLogs", headers=HEADERS)
        )
    orders = orders_resp.json().get("records", [])
    logs = logs_resp.json().get("records", [])
    statuses = [r["fields"].get("status", "") for r in orders]
    total = len(orders)
    success = sum(1 for s in statuses if s in ("Reserved", "Completed", "Shipped"))
    return _set("metrics", {
        "total_orders": total,
        "total_audit_logs": len(logs),
        "success_rate": round(success / total * 100, 1) if total else 0,
        "orders_by_status": {s: statuses.count(s) for s in set(statuses)}
    })