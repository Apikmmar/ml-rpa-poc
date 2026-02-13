# RPA Automation API

Simple FastAPI backend + HTML frontend to trigger Airtable automations.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Airtable credentials:
```bash
copy .env.example .env
```
Edit `.env` and add your Airtable token and base ID.

3. Run the backend:
```bash
uvicorn main:app --reload
```

4. Open frontend:
Open `index.html` in your browser.

## API Endpoints

- `POST /orders` - Create order (triggers Order Validator)
- `GET /orders` - List all orders
- `PATCH /orders/{id}/status` - Update order status (triggers Stock Checker/Picklist Generator)
- `GET /picklists` - List picklists
- `PATCH /picklists/{id}/status` - Update picklist (triggers Picklist Started/Completer)
- `POST /stock-transfers` - Create transfer (triggers Transfer Approval)
- `GET /stocks` - List stocks
- `GET /exceptions` - List exceptions
- `GET /audit-logs` - List audit logs

## Automation Flow

1. Create Order → Order Validator automation
2. Status=Validated → Stock Checker automation
3. Status=Stock Confirmed → Picklist Generator automation
4. Picklist Status=In Progress → Picklist Started automation
5. Picklist Status=Completed → Picklist Completer automation
