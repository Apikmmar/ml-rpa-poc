from fastapi import APIRouter, HTTPException
import httpx
from config import BASE_URL, HEADERS

router = APIRouter(tags=["monitoring"])

@router.get("/exceptions")
async def list_exceptions():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Exceptions", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@router.get("/audit-logs")
async def list_audit_logs():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/AuditLogs", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@router.get("/backorders")
async def list_backorders():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Backorders", headers=HEADERS)
        return resp.json()

@router.get("/notifications")
async def list_notifications():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Notifications", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@router.get("/metrics/dashboard")
async def get_metrics():
    async with httpx.AsyncClient() as client:
        orders_resp = await client.get(f"{BASE_URL}/Orders", headers=HEADERS)
        logs_resp = await client.get(f"{BASE_URL}/AuditLogs", headers=HEADERS)

    orders = orders_resp.json().get("records", [])
    logs = logs_resp.json().get("records", [])

    statuses = [r["fields"].get("status", "") for r in orders]
    total = len(orders)
    success = sum(1 for s in statuses if s in ("Reserved", "Completed", "Shipped"))

    return {
        "total_orders": total,
        "total_audit_logs": len(logs),
        "success_rate": round(success / total * 100, 1) if total else 0,
        "orders_by_status": {s: statuses.count(s) for s in set(statuses)}
    }
