from fastapi import APIRouter, HTTPException, Query
import httpx
import json
import asyncio
from datetime import datetime, timedelta
from config import BASE_URL, HEADERS

router = APIRouter(prefix="/reports", tags=["reports"])

_reports_cache = {"data": None, "cached_at": None}
CACHE_TTL = 86400

SORT_PARAMS = "?sort[0][field]=created_at&sort[0][direction]=desc"

async def _fetch_reports():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Reports{SORT_PARAMS}", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        _reports_cache["data"] = resp.json()
        _reports_cache["cached_at"] = datetime.utcnow().timestamp()
        return _reports_cache["data"]

async def _save_report(client, report_type, data):
    now = datetime.utcnow().isoformat()
    payload = {
        "fields": {
            "report_type": report_type, 
            "report_data": json.dumps(data), 
            "generated_by": "System", 
            "status": "Generated", 
            "created_at": now, 
            "created_by": "System", 
            "updated_at": now, 
            "updated_by": "System"
            }
        }
    resp = await client.post(f"{BASE_URL}/Reports", headers=HEADERS, json=payload)
    return resp.json()["id"]

@router.get("/reconciliation")
async def stock_reconciliation():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Stocks", headers=HEADERS)
        stocks = resp.json()["records"]
        report = [{
            "sku": s["fields"]["sku"], 
            "quantity": s["fields"].get("quantity", 0), 
            "available": s["fields"].get("available", 0), 
            "reserved": s["fields"].get("reserved", 0)
        } for s in stocks]
        
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
        orders_resp, picklists_resp, exceptions_resp, backorders_resp = await asyncio.gather(
            client.get(f"{BASE_URL}/Orders?filterByFormula=IS_AFTER({{created_at}},'{since}')", headers=HEADERS),
            client.get(f"{BASE_URL}/Picklists?filterByFormula=IS_AFTER({{created_at}},'{since}')", headers=HEADERS),
            client.get(f"{BASE_URL}/Exceptions?filterByFormula=IS_AFTER({{created_at}},'{since}')", headers=HEADERS),
            client.get(f"{BASE_URL}/Backorders?filterByFormula=IS_AFTER({{created_at}},'{since}')", headers=HEADERS),
        )
        orders = orders_resp.json().get("records", [])
        picklists = picklists_resp.json().get("records", [])
        exceptions = exceptions_resp.json().get("records", [])
        backorders = backorders_resp.json().get("records", [])
        statuses = [o["fields"].get("status", "") for o in orders]
        priorities = [o["fields"].get("priority", "") for o in orders]
        report = {
            "date": datetime.utcnow().date().isoformat(),
            "total_orders": len(orders),
            "by_status": {s: statuses.count(s) for s in set(statuses)},
            "by_priority": {p: priorities.count(p) for p in set(priorities)},
            "picklists_generated": len(picklists),
            "exceptions_raised": len(exceptions),
            "backorders_created": len(backorders),
        }
        report_id = await _save_report(client, "Daily Summary", report)
        return {"report_id": report_id, "report": report}

@router.post("/weekly")
async def weekly_summary():
    async with httpx.AsyncClient() as client:
        since = (datetime.utcnow() - timedelta(days=7)).isoformat()
        orders_resp, stocks_resp, receipts_resp, exceptions_resp, backorders_resp = await asyncio.gather(
            client.get(f"{BASE_URL}/Orders?filterByFormula=IS_AFTER({{created_at}},'{since}')", headers=HEADERS),
            client.get(f"{BASE_URL}/Stocks", headers=HEADERS),
            client.get(f"{BASE_URL}/Good_Receipts?filterByFormula=IS_AFTER({{created_at}},'{since}')", headers=HEADERS),
            client.get(f"{BASE_URL}/Exceptions?filterByFormula=IS_AFTER({{created_at}},'{since}')", headers=HEADERS),
            client.get(f"{BASE_URL}/Backorders?filterByFormula=IS_AFTER({{created_at}},'{since}')", headers=HEADERS),
        )
        orders = orders_resp.json().get("records", [])
        stocks = stocks_resp.json().get("records", [])
        receipts = receipts_resp.json().get("records", [])
        exceptions = exceptions_resp.json().get("records", [])
        backorders = backorders_resp.json().get("records", [])
        statuses = [o["fields"].get("status", "") for o in orders]
        priorities = [o["fields"].get("priority", "") for o in orders]
        fulfilled = statuses.count("Fulfilled")
        total_received = sum(r["fields"].get("quantity", 0) for r in receipts)
        report = {
            "week_ending": datetime.utcnow().date().isoformat(),
            "total_orders": len(orders),
            "by_status": {s: statuses.count(s) for s in set(statuses)},
            "by_priority": {p: priorities.count(p) for p in set(priorities)},
            "fulfillment_rate": round(fulfilled / len(orders) * 100, 1) if orders else 0,
            "total_skus": len(stocks),
            "low_stock": [s["fields"]["sku"] for s in stocks if s["fields"].get("available", 0) < 10],
            "goods_receipts": len(receipts),
            "total_stock_received": total_received,
            "exceptions_raised": len(exceptions),
            "backorders_created": len(backorders),
        }
        report_id = await _save_report(client, "Weekly Summary", report)
        return {"report_id": report_id, "report": report}

@router.get("")
async def list_reports(refresh: bool = Query(False)):
    now_ts = datetime.utcnow().timestamp()
    cache_stale = (
        _reports_cache["data"] is None or
        _reports_cache["cached_at"] is None or
        (now_ts - _reports_cache["cached_at"]) > CACHE_TTL
    )
    if refresh or cache_stale:
        return await _fetch_reports()
    return _reports_cache["data"]
