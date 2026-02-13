from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import orders, stocks, picklists, transfers, reports, monitoring
from config import AIRTABLE_BASE_ID, AIRTABLE_TOKEN, BASE_URL
import os

app = FastAPI(title="RPA Automation API", version="1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(orders.router)
app.include_router(stocks.router)
app.include_router(picklists.router)
app.include_router(transfers.router)
app.include_router(reports.router)
app.include_router(monitoring.router)

@app.get("/api")
def root():
    return {"message": "RPA Automation API", "version": "1.0"}

@app.get("/api/config")
def get_config():
    return {"base_id": AIRTABLE_BASE_ID, "token_set": "Yes" if AIRTABLE_TOKEN != "your_token" else "No", "base_url": BASE_URL}

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
