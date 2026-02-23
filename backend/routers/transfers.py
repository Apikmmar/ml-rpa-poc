from fastapi import APIRouter, HTTPException
import httpx
from datetime import datetime
from config import BASE_URL, HEADERS

router = APIRouter(prefix="/stock-transfers", tags=["transfers"])

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
async def list_stock_transfers():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Stock_Transfers", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()
