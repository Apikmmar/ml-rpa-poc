from fastapi import APIRouter, HTTPException
import httpx
import json
from datetime import datetime
from config import BASE_URL, HEADERS

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/reconciliation")
async def stock_reconciliation():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Stocks", headers=HEADERS)
        stocks = resp.json()["records"]
        report = [{"sku": s["fields"]["sku"], "quantity": s["fields"].get("quantity", 0), "available": s["fields"].get("available", 0), "reserved": s["fields"].get("reserved", 0)} for s in stocks]
        now = datetime.utcnow().isoformat()
        report_payload = {"fields": {"report_type": "Stock Reconciliation", "report_data": json.dumps(report), "generated_by": "System", "status": "Generated", "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
        report_resp = await client.post(f"{BASE_URL}/Reports", headers=HEADERS, json=report_payload)
        return {"report_id": report_resp.json()["id"], "report": report, "total_items": len(report)}

@router.get("")
async def list_reports():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Reports", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()
