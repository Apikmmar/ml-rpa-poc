# ML RPA POC - Warehouse Automation System

Airtable-based RPA system for warehouse order fulfillment automation with FastAPI backend and HTML/JS frontend.

## Project Structure

```
ml-rpa-poc/
├── backend/              # FastAPI backend
│   ├── routers/          # API route modules
│   ├── models/           # Pydantic schemas
│   ├── config.py         # Configuration
│   ├── main.py           # App entry point
│   └── .env              # Environment variables
├── frontend/             # HTML/CSS/JS frontend
│   ├── pages/            # HTML pages (7 pages)
│   ├── js/               # JavaScript modules
│   └── css/              # Stylesheets
├── docs/                 # Documentation
│   ├── airtable-schema.txt
│   ├── requirements.txt
│   └── frontend-coverage.md
├── .env                  # Root environment variables
├── .env.example          # Example configuration
└── requirements.txt      # Python dependencies
```

## Quick Start

### Backend Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Airtable credentials:
# AIRTABLE_TOKEN=your_token
# AIRTABLE_BASE_ID=your_base_id
```

3. Run backend:
```bash
cd backend
uvicorn main:app --reload
```

Backend: http://localhost:8000

### Frontend Setup

Serve the frontend:
```bash
cd frontend
python -m http.server 8080
```

Frontend: http://localhost:8080/pages/index.html

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features

### Backend (20 Endpoints)
- **Orders**: Create, list, get by ID, update status
- **Stocks**: List, goods receipt, receipts history
- **Picklists**: List, update status, optimize route, generate QR
- **Transfers**: Create, list stock transfers
- **Reports**: Stock reconciliation, list reports
- **Monitoring**: Exceptions, audit logs, backorders, notifications, metrics

### Frontend (7 Pages - 100% Coverage)
- **Dashboard**: Home page with navigation
- **Orders**: Create orders with items, view all orders, update status
- **Stocks**: View inventory, receive goods, track receipts
- **Picklists**: Manage picklists, optimize routes, generate QR codes
- **Transfers**: Create and track stock transfers
- **Reports**: Generate reconciliation reports, view history
- **Monitoring**: Metrics dashboard, exceptions, logs, backorders, notifications

### Airtable (12 Tables + 19 Automations)
- Orders, Stocks, Order_Items, Picklists, Stock_Transfers
- Exceptions, Notifications, Backorders, Goods_Receipts, Reports
- AuditLogs, Notifications
- Automated workflows for validation, stock checking, picklist generation, transfers, backorder fulfillment

## Architecture

```
Frontend (HTML/JS) → FastAPI Backend → Airtable API → Airtable Database + Automations
```

- **Frontend**: Pure HTML/CSS/JS with modular design
- **Backend**: FastAPI with modular routers, async HTTP client
- **Database**: Airtable with formulas, rollups, and automations
- **Automations**: 19 Airtable automations (free tier compatible)

## Documentation

See `docs/` folder:
- `airtable-schema.txt` - Complete database schema and automations
- `requirements.txt` - Original RPA requirements
- `frontend-coverage.md` - Frontend endpoint coverage

## Tech Stack

- **Backend**: Python 3.x, FastAPI, httpx, python-dotenv
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: Airtable (Free Tier)
- **API**: RESTful with async operations
