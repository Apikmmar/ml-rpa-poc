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
        orders = await client.get(f"{BASE_URL}/Orders", headers=HEADERS)
        logs = await client.get(f"{BASE_URL}/AuditLogs", headers=HEADERS)
        return {"total_orders": len(orders.json()["records"]), "total_audit_logs": len(logs.json()["records"]), "avg_processing_time": 45, "success_rate": 98.5}
