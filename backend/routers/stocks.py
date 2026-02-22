from fastapi import APIRouter, HTTPException
import httpx
from datetime import datetime
from config import BASE_URL, HEADERS

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("")
async def list_stocks():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Stocks", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@router.get("/{stock_id}")
async def get_stock(stock_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Stocks/{stock_id}", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()
        f = data.get("fields", {})
        return {
            "stock_id": stock_id, 
            "sku": f.get("sku"), 
            "available": f.get("available", 0), 
            "quantity": f.get("quantity", 0), 
            "reserved": f.get("reserved", 0), 
            "location": f.get("location"), 
            "rack": f.get("rack")
        }

@router.post("/goods-receipt")
async def receive_goods(sku: str, quantity: int, location: str, rack: str, received_by: str = "System"):
    async with httpx.AsyncClient() as client:
        stocks = await client.get(f"{BASE_URL}/Stocks?filterByFormula={{sku}}='{sku}'", headers=HEADERS)
        stock_data = stocks.json()
        if stock_data["records"]:
            stock_id = stock_data["records"][0]["id"]
            now = datetime.utcnow().isoformat()
            
            receipt_payload = {"fields": {"link_sku": [stock_id], "quantity": quantity, "location": location, "rack": rack, "received_by": received_by, "status": "Completed", "created_at": now, "created_by": received_by, "updated_at": now, "updated_by": received_by}}
            receipt_resp = await client.post(f"{BASE_URL}/Good_Receipts", headers=HEADERS, json=receipt_payload)
            
            if receipt_resp.status_code != 200:
                raise HTTPException(status_code=receipt_resp.status_code, detail=receipt_resp.text)
            
            current_add = stock_data["records"][0]["fields"].get("add_stock", 0)
            stock_payload = {"fields": {"add_stock": current_add + quantity, "updated_at": now, "updated_by": received_by}}
            await client.patch(f"{BASE_URL}/Stocks/{stock_id}", headers=HEADERS, json=stock_payload)
            
            return {
                "receipt_id": receipt_resp.json().get("id"), 
                "status": "received", "sku": sku, 
                "quantity": quantity, 
                "location": location, 
                "rack": rack
            }
    raise HTTPException(404, "SKU not found")

@router.get("/goods-receipts")
async def list_goods_receipts():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/Good_Receipts", headers=HEADERS)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()
