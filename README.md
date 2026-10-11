# ThermaGuard

ThermaGuard contains a React/Vite dashboard and a FastAPI service. The Vite development server proxies `/api/*` requests to FastAPI at `http://127.0.0.1:8000`.

## Run locally

Use two terminals from the ThermaGuard project folder.

### 1. Start FastAPI

```bash
cd backend/backend
python3 -m venv ../.venv
../.venv/bin/python -m pip install -r requirements.txt
../.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

On Windows, use `..\.venv\Scripts\python.exe` and `..\.venv\Scripts\uvicorn.exe` instead of the `.venv/bin` paths.

Check the service at [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health) and browse the API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 2. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually [http://localhost:5173](http://localhost:5173). Keep the backend terminal running too. The top bar reports whether FastAPI is reachable; live temperature and humidity load from the backend weather endpoint when available.

## Run the backend with AWS SAM locally

The SAM option runs the API inside a local Lambda simulator. It does not create AWS cloud resources. Install Docker Desktop and the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html), then start Docker Desktop.

In terminal 1:

```bash
cd backend/backend
sam build --use-container
sam local start-api --port 8000
```

In terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, usually [http://localhost:5173](http://localhost:5173). Check the API at [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health). The SAM template stores its demo SQLite database in the local Lambda container's `/tmp`, so saved plans are only for local demonstration. Do not run `sam deploy` if you want to avoid creating AWS resources and charges.

## Checks

```bash
# From frontend/
npm run lint
npm run build

# From backend/backend/
../.venv/bin/python -m pytest -q
```

## Current data coverage

FastAPI currently provides the Delhi pilot zone dataset, current weather, an explainable risk endpoint, scenario evaluation, and saved action plans. The city-specific dashboard risk scores, alerts, forecast, and several display metrics remain illustrative frontend data. The backend deliberately returns `insufficient_data` for a calculated risk score until verified heat indicators are available.
