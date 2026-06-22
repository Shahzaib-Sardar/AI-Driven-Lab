# Vercel Deployment Guide

## Overview
This guide explains how to deploy the Expense Tracking App on Vercel.

## Frontend Deployment (Vercel)

The frontend is a React + Vite application that can be deployed on Vercel.

### Prerequisites
1. Vercel account (https://vercel.com)
2. GitHub repository connected to Vercel
3. Backend deployed (see Backend Deployment)

### Step 1: Configure Environment Variables in Vercel

1. Go to your Vercel Project Dashboard
2. Navigate to **Settings → Environment Variables**
3. Add the following variable:
   ```
   Name: VITE_API_BASE
   Value: https://your-backend-url.com/api
   ```
   Replace `https://your-backend-url.com/api` with your actual backend URL

### Step 2: Deploy
Vercel automatically deploys when you push to the main branch. The `vercel.json` configuration handles:
- Installing frontend dependencies
- Running the build command
- Serving the frontend from the `frontend/dist` directory
- Handling SPA routing with rewrites

### Step 3: Verify Deployment
After deployment:
1. Visit your Vercel deployment URL
2. Try signing up or logging in
3. Check browser console for any API errors
4. Ensure the API_BASE URL is correctly set by inspecting the network tab

## Backend Deployment Options

### Option 1: Railway.app (Recommended)
1. Push your code to GitHub
2. Go to Railway.app and connect your GitHub repo
3. Add a `Procfile` in the backend directory:
   ```
   web: python backend/run.py
   ```
4. Set environment variables:
   - `FLASK_ENV=production`
   - `OPENAI_API_KEY=your_key` (if using AI features)

### Option 2: Render
1. Create a Render account (https://render.com)
2. Create a new Web Service
3. Connect your GitHub repo
4. Set the build command: `pip install -r backend/requirements.txt`
5. Set the start command: `python backend/run.py`

### Option 3: Heroku
1. Install Heroku CLI
2. Run:
   ```
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

## Troubleshooting

### Issue: `vite: command not found`
**Solution:** The `vercel.json` now explicitly installs dependencies in the frontend directory before building.

### Issue: API calls fail with CORS errors
**Solution:** Ensure your backend has CORS enabled:
```python
from flask_cors import CORS
CORS(app)
```

### Issue: `Cannot POST /api/auth/login`
**Solution:** 
1. Verify the backend is deployed and running
2. Check that `VITE_API_BASE` environment variable is set correctly in Vercel
3. Ensure the backend URL is accessible (no firewall blocking)

### Issue: Blank page after deployment
**Solution:**
1. Check browser console for JavaScript errors
2. Verify the API_BASE URL in Network tab
3. Ensure `frontend/dist` is the correct output directory

## Environment Variables Reference

| Variable | Frontend | Backend | Description |
|----------|----------|---------|-------------|
| VITE_API_BASE | ✓ | - | Base URL for API calls (e.g., https://api.example.com/api) |
| FLASK_ENV | - | ✓ | Set to `production` for deployments |
| OPENAI_API_KEY | - | ✓ | OpenAI API key for AI summary features |
| SECRET_KEY | - | ✓ | Flask secret key for sessions (set in deployment) |

## Local Testing Before Deployment

Before deploying, test locally:

1. **Build the frontend:**
   ```bash
   cd frontend
   npm run build
   npm run preview
   ```

2. **Run the backend:**
   ```bash
   cd backend
   python run.py
   ```

3. **Test the full flow** in the preview server

## Post-Deployment Checklist

- [ ] Frontend builds without errors
- [ ] Environment variables are set in Vercel
- [ ] Backend is deployed and running
- [ ] Can sign up / login
- [ ] Can create transactions
- [ ] Can generate AI summary (if backend has OPENAI_API_KEY)
- [ ] No CORS errors in browser console
- [ ] All network requests go to the correct API URL

## Git Deployment Notes

- The `vercel.json` configuration overrides the default Next.js detection
- The `.vercelignore` file excludes backend files to reduce build time
- Vercel will rebuild automatically on each push to `main` branch

For more help, see:
- Vercel Docs: https://vercel.com/docs
- Vite Docs: https://vitejs.dev/
- Flask Docs: https://flask.palletsprojects.com/
