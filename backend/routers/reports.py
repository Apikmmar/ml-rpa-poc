from fastapi import APIRouter, HTTPException
import httpx
import json
from datetime import datetime, timedelta
from config import BASE_URL, HEADERS

router = APIRouter(prefix="/reports", tags=["reports"])

async def _save_report(client, report_type, data):
    now = datetime.utcnow().isoformat()
    payload = {"fields": {"report_type": report_type, "report_data": json.dumps(data), "generated_by": "System", "status": "Generated", "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
    resp = await client.post(f"{BASE_URL}/Reports", headers=HEADERS, json=payload)
    return resp.json()["id"]

@router.get("/reconciliation")
async def stock_reconciliation():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Stocks", headers=HEADERS)
        stocks = resp.json()["records"]
        report = [{"sku": s["fields"]["sku"], "quantity": s["fields"].get("quantity", 0), "available": s["fields"].get("available", 0), "reserved": s["fields"].get("reserved", 0)} for s in stocks]
        report_id = await _save_report(client, "Stock Reconciliation", report)
        return {
            "report_id": report_id, 
            "report": report, 
            "total_items": len(report)
        }

@router.post("/daily")
async def daily_summary():
    async with httpx.AsyncClient() as client:
        since = (datetime.utcnow() - timedelta(days=1)).isoformat()
        orders_resp = await client.get(f"{BASE_URL}/Orders?filterByFormula=IS_AFTER({{created_at}},'{since}')", headers=HEADERS)
        orders = orders_resp.json().get("records", [])
        statuses = [o["fields"].get("status", "") for o in orders]
        report = {"date": datetime.utcnow().date().isoformat(), "total_orders": len(orders), "by_status": {s: statuses.count(s) for s in set(statuses)}}
        report_id = await _save_report(client, "Daily Summary", report)
        return {
            "report_id": report_id, 
            "report": report
        }

@router.post("/weekly")
async def weekly_summary():
    async with httpx.AsyncClient() as client:
        since = (datetime.utcnow() - timedelta(days=7)).isoformat()
        orders_resp = await client.get(f"{BASE_URL}/Orders?filterByFormula=IS_AFTER({{created_at}},'{since}')", headers=HEADERS)
        stocks_resp = await client.get(f"{BASE_URL}/Stocks", headers=HEADERS)
        orders = orders_resp.json().get("records", [])
        stocks = stocks_resp.json().get("records", [])
        statuses = [o["fields"].get("status", "") for o in orders]
        report = {"week_ending": datetime.utcnow().date().isoformat(), "total_orders": len(orders), "by_status": {s: statuses.count(s) for s in set(statuses)}, "total_skus": len(stocks), "low_stock": [s["fields"]["sku"] for s in stocks if s["fields"].get("avb_qty", 0) < 10]}
        report_id = await _save_report(client, "Weekly Summary", report)
        return {
            "report_id": report_id, 
            "report": report
        }

@router.get("")
async def list_reports():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Reports", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()
