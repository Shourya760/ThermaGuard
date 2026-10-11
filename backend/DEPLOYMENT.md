# CoolBlock Deployment Guide

This guide covers preparing the CoolBlock FastAPI backend for deployment to common cloud providers (e.g., Heroku, Render, AWS AppRunner, Docker).

## 1. Environment Variables Configuration

Before deploying, ensure your environment variables are configured. Use the provided `backend/.env.example` as a template for your production settings.

### Critical Variables:
- **`APP_ENV`**: Set to `production`.
- **`CORS_ORIGINS`**: Provide a comma-separated list of your allowed frontend origins (e.g., `https://your-frontend-domain.com`). Do not use the `*` wildcard when credentials are allowed.
- **`DATABASE_URL`**: 
  - **WARNING:** By default, CoolBlock uses a local SQLite database (`sqlite:///./coolblock.db`).
  - In ephemeral cloud deployments (like Heroku or Render without disk mounts), a local SQLite file **will NOT persist** across restarts. For true durable production persistence, provision a managed PostgreSQL database and set `DATABASE_URL` to its connection string (e.g., `postgresql://user:password@host:5432/coolblock`).

## 2. Startup Command

Most deployment platforms inject a `PORT` environment variable. Ensure you bind the application to `0.0.0.0` and the assigned `$PORT`.

Use the following startup command in your `Procfile`, `start` script, or Docker command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## 3. Health Check

Configure your deployment platform's health checks to point to:
- **Endpoint:** `GET /api/health`
- **Expected Response:** `200 OK` (`{"status": "ok", "env": "production"}`)

## 4. Git Initialization and Deployment

To push this project to a new GitHub repository:

```bash
# Initialize git in the root coolblock folder
git init

# Add all files (the .gitignore ensures secrets and databases aren't committed)
git add .

# Commit your code
git commit -m "Initial commit for CoolBlock"

# Rename branch to main
git branch -M main

# Add your GitHub remote (replace with your actual URL)
git remote add origin https://github.com/your-username/coolblock.git

# Push the code
git push -u origin main
```

## 5. Troubleshooting
- **CORS Errors:** Verify that the frontend domain exactly matches the value in `CORS_ORIGINS` (including `http` or `https` and excluding trailing slashes).
- **Data Loss on Restart:** If action plans vanish when the app restarts, it means you're using SQLite on an ephemeral filesystem. Switch to a managed database (PostgreSQL) and update `DATABASE_URL`.
- **Port Binding Issues:** Ensure the application is bound to `0.0.0.0` rather than `127.0.0.1` so the cloud platform's router can reach it.
