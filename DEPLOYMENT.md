# Deployment Guide - Render (Free)

## Prerequisites
1. GitHub account
2. Render account (https://render.com)
3. Push your code to GitHub

## Deploy Backend (FastAPI)

1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: ml-rpa-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Add Environment Variables:
   - `AIRTABLE_TOKEN` = your_token
   - `AIRTABLE_BASE_ID` = your_base_id
6. Click "Create Web Service"
7. Copy your backend URL (e.g., https://ml-rpa-backend.onrender.com)

## Deploy Frontend (Static Site)

1. Go to Render Dashboard
2. Click "New +" → "Static Site"
3. Connect your GitHub repo
4. Configure:
   - **Name**: ml-rpa-frontend
   - **Build Command**: (leave empty)
   - **Publish Directory**: `frontend`
   - **Plan**: Free
5. Click "Create Static Site"
6. Your frontend URL: https://ml-rpa-frontend.onrender.com

## Update Frontend API URL

After backend is deployed, update `frontend/js/api.js`:

```javascript
const API_URL = 'https://ml-rpa-backend.onrender.com';
```

Then push to GitHub - Render will auto-redeploy!

## Important Notes

- **Free tier limitations**:
  - Backend spins down after 15 min inactivity
  - First request after sleep takes ~30 seconds (cold start)
  - 750 hours/month free

- **Custom Domain** (Optional):
  - Both services support custom domains for free
  - Add in service settings

## Alternative: Deploy Both Together

If you want ONE deployment, modify `backend/main.py` to serve static files:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

Then deploy only the backend service and access everything at one URL!

## Troubleshooting

- **Backend not starting**: Check environment variables are set
- **CORS errors**: Ensure CORS is configured in `backend/main.py`
- **Frontend can't reach backend**: Update API_URL in `frontend/js/api.js`
