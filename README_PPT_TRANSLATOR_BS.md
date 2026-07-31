# PPT Translator BS MVP

This implementation converts the desktop PPT translator workflow into a browser-based architecture:

- **Backend:** FastAPI (`/backend`)
- **Frontend:** Next.js (`/frontend`)
- **Deployment:** Docker Compose (`/docker-compose.yml`)

## MVP Scope

- Upload `.pptx` from browser
- Configure endpoint/model/api key/languages
- Backend performs batched translation and writes translated PPTX
- Browser downloads translated result
- No login/auth (as requested)

## Run with Docker

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`

## Local Run (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000 npm run dev
```

## API

`POST /api/v1/translate/pptx`

Multipart form fields:
- `file`: input `.pptx`
- `options_json`: JSON string matching backend `TranslationOptions`

Response:
- translated `.pptx` file stream
