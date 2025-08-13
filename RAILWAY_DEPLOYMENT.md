# 🚀 Railway Deployment Guide

## Backend Deployment (Railway)

1. **Go to railway.app** → Sign up with GitHub
2. **New Project** → **Deploy from GitHub**
3. **Select repo**: `adptx_law_mvp`
4. **Settings** → **Environment Variables**:
   - `GROQ_API_KEY` = your Groq API key
   - `INDIAN_KANOON_API_KEY` = your Indian Kanoon API key
5. **Deploy** ✅

## Frontend Deployment (Vercel)

1. **Already deployed on Vercel** ✅
2. **Update config.js** with Railway backend URL
3. **Push changes** → Auto-deploys

## Connect Frontend to Backend

1. **Get Railway URL** from dashboard
2. **Update frontend/public/config.js**:
   ```javascript
   window.configs = {
       apiUrl: 'https://your-railway-app.railway.app',
   };
   ```
3. **Push to GitHub** → Vercel auto-deploys

## Test

1. **Frontend**: Your Vercel URL
2. **Backend Health**: `https://your-railway-app.railway.app/api/health`
3. **Chat**: Test the full system

## Files Added for Railway

- `railway.json` - Railway configuration
- `backend/Procfile` - Start command
- `backend/runtime.txt` - Python version
- `RAILWAY_DEPLOYMENT.md` - This guide
