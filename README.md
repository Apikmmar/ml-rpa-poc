# ML RPA POC - Warehouse Automation System

Airtable + FastAPI RPA system for warehouse order fulfillment automation with HTML/JS frontend and AWS Lambda sync infrastructure.

## Project Structure

```
ml-rpa-poc/
├── backend/                  # FastAPI backend
│   ├── routers/              # API route modules
│   ├── models/               # Pydantic schemas
│   ├── config.py             # Configuration
│   ├── main.py               # App entry point
│   └── .env                  # Environment variables
├── frontend/                 # HTML/CSS/JS frontend
│   ├── pages/                # HTML pages (7 pages)
│   ├── js/                   # JavaScript modules
│   └── css/                  # Stylesheets
├── lambda_functions/
│   ├── SyncAirtableData/     # Weekly Airtable → DynamoDB sync
│   └── ProcessOrdersCSV/     # S3 CSV → FastAPI order creation
├── ml_rpa_poc/               # CDK infrastructure
│   ├── config.py             # PREFIX constant
│   ├── dynamo_db_stack.py    # DynamoDB tables
│   ├── lambda_function_stack.py
│   └── ml_rpa_poc_stack.py
├── layers/httpx/             # Lambda httpx layer
├── docs/                     # Documentation
├── .env.example
└── requirements.txt
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

```bash
cd frontend
python -m http.server 8080
```

Frontend: http://localhost:8080/pages/index.html

### AWS CDK Deploy

```bash
pip install -r requirements.txt
cdk deploy
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features

### Backend (25 Endpoints)
- **Orders**: Create, list, get by ID, update status+ETA, reserve stock
- **Stocks**: List, get by ID, goods receipt, receipts history
- **Picklists**: List, update status, optimize route
- **Transfers**: Create, list stock transfers
- **Reports**: Stock reconciliation, daily summary, weekly summary, list reports
- **Monitoring**: Exceptions (GET/POST), audit logs, backorders, notifications, metrics dashboard

### Frontend (7 Pages - 100% Coverage)
- **Dashboard**: Home page with navigation
- **Orders**: Create orders, view all orders, update status with ETA
- **Stocks**: View inventory, receive goods, track receipts
- **Picklists**: Manage picklists, optimize routes
- **Transfers**: Create and track stock transfers
- **Reports**: Stock reconciliation, daily summary, weekly summary, view history
- **Monitoring**: Metrics dashboard, exceptions, audit logs, backorders, notifications

### Airtable (12 Tables + 19 Automations)
- Orders, Stocks, Order_Items, Picklists, Stock_Transfers
- Exceptions, Notifications, Backorders, Good_Receipts, Reports, AuditLogs
- 19 automated workflows: order validation, stock checking, picklist generation, transfer approval, backorder fulfillment, exception handling, scheduled cleanup

### AWS Infrastructure
- **S3**: `s3-ml-rpa-poc` bucket — CSV uploads trigger order processing
- **Lambda**: `RPA-ProcessOrdersCSV` — reads `orders/*.csv`, creates orders via FastAPI, moves file to `processed/`
- **Lambda**: `RPA-SyncAirtableData` — weekly sync of all Airtable tables to DynamoDB
- **DynamoDB**: 10 tables as read replica (prefixed `RPA-`)
- **EventBridge**: Weekly schedule for Airtable sync
- **X-Ray + Powertools**: Tracing and structured logging on all Lambdas

## Architecture

```
Frontend (HTML/JS) → FastAPI Backend → Airtable API → Airtable Database + Automations
                                                                ↓ (weekly sync)
S3 (orders/*.csv) → ProcessOrdersCSV Lambda → FastAPI      DynamoDB (read replica)
```

## Production Path (Full AWS)

To go fully serverless on AWS (abandon Airtable):
- **25 API Gateway + Lambda** functions (replace FastAPI endpoints)
- **20 backend Lambdas** (replace 19 Airtable automations + 1 SES notification sender)
- **DynamoDB Streams** to trigger event-driven Lambdas
- **SES** to replace Airtable Gmail automations
- **Total: ~45 Lambdas**, 1 API Gateway, DynamoDB as primary database

## Tech Stack

- **Backend**: Python 3.x, FastAPI, httpx, tenacity, python-dotenv
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: Airtable (Free Tier) + DynamoDB (sync replica)
- **Infrastructure**: AWS CDK, Lambda, S3, EventBridge, X-Ray
- **Region**: ap-southeast-1
