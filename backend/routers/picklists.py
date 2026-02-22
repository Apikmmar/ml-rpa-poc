from fastapi import APIRouter, HTTPException
import httpx
from config import BASE_URL, HEADERS
from models.schemas import UpdateStatusRequest

router = APIRouter(prefix="/picklists", tags=["picklists"])

@router.get("")
async def list_picklists():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Picklists", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

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
    return {
        "picklist_id": picklist_id, 
        "optimized_route": ["Zone-A/Rack-1", "Zone-A/Rack-2", "Zone-B/Rack-1", "Zone-C/Rack-3"]
    }

@router.get("/{picklist_id}/qr")
async def generate_qr(picklist_id: str):
    return {
        "picklist_id": picklist_id, 
        "qr_data": f"PICKLIST-{picklist_id}"
    }
