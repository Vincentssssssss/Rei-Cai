# PPT Translator BS MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the uploaded desktop PPT translator into a browser-based MVP with FastAPI backend, Next.js frontend, and Docker deployment.

**Architecture:** Split into two services. Backend handles PPT parsing, batch translation calls, and PPT write-back. Frontend provides a single-page workflow for config + upload + download. Docker Compose orchestrates both services.

**Tech Stack:** Python 3.11, FastAPI, python-pptx, requests, pytest, Next.js 14 (App Router), TypeScript, Docker Compose

## Global Constraints

- Keep MVP scope: no login, no license system, no desktop UI.
- Preserve paragraph formatting with safe run replacement logic.
- Support batch translation via backend prompt batching.
- Separate frontend and backend processes.
- Provide containerized deployment with one command.

---

### Task 1: Scaffold backend service

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/config.py`
- Create: `backend/requirements.txt`
- Create: `backend/pytest.ini`

**Interfaces:**
- Produces: `create_app() -> FastAPI` entrypoint and typed request model for translation options.

- [ ] **Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_api.py::test_health -v`
Expected: FAIL because backend app module does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_api.py::test_health -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend
git commit -m "feat: scaffold fastapi backend service"
```

### Task 2: Implement PPT translation core and API endpoint

**Files:**
- Create: `backend/app/services/translator.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_translator.py`

**Interfaces:**
- Consumes: `TranslationOptions` schema.
- Produces: `translate_pptx(input_path: str, output_path: str, options: TranslationOptions) -> None`

- [ ] **Step 1: Write failing tests**

```python
def test_parse_batch_json_robust_extracts_translations():
    raw = '{"translations":[{"text":"A"},{"text":"B"}]}'
    out = parse_batch_json_robust(raw, 2)
    assert out == ["A", "B"]
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest backend/tests/test_translator.py -v`
Expected: FAIL because function is undefined.

- [ ] **Step 3: Implement translation service**

```python
def parse_batch_json_robust(raw: str, expected_n: int) -> Optional[List[str]]:
    ...
```

- [ ] **Step 4: Run tests to verify pass**

Run: `pytest backend/tests/test_translator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend
git commit -m "feat: add ppt translation service and endpoint"
```

### Task 3: Build Next.js frontend upload workflow

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/next.config.js`
- Create: `frontend/tsconfig.json`
- Create: `frontend/app/page.tsx`
- Create: `frontend/app/globals.css`
- Create: `frontend/components/translator-form.tsx`

**Interfaces:**
- Consumes: `POST /api/v1/translate/pptx` backend endpoint.
- Produces: browser download for translated PPTX.

- [ ] **Step 1: Write minimal UI behavior test placeholder**

```text
Document manual smoke scenario in README for submit/download workflow.
```

- [ ] **Step 2: Run lint/build to verify failing baseline**

Run: `npm run build`
Expected: FAIL before implementation.

- [ ] **Step 3: Implement frontend form and API call**

```tsx
async function onSubmit(...) {
  const formData = new FormData();
  ...
}
```

- [ ] **Step 4: Run build to verify pass**

Run: `npm run build`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend
git commit -m "feat: add nextjs frontend for ppt translation"
```

### Task 4: Dockerize and document deployment

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`
- Create: `README_PPT_TRANSLATOR_BS.md`

**Interfaces:**
- Produces: `docker compose up --build` runnable deployment.

- [ ] **Step 1: Write verification command first**

```bash
docker compose config
```

- [ ] **Step 2: Run to verify baseline/failure if needed**

Run: `docker compose config`
Expected: Parse output without errors after files exist.

- [ ] **Step 3: Implement Docker files + docs**

```dockerfile
FROM python:3.11-slim
...
```

- [ ] **Step 4: Run compose config/build validation**

Run: `docker compose config && docker compose build`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml backend/Dockerfile frontend/Dockerfile README_PPT_TRANSLATOR_BS.md
git commit -m "feat: dockerize bs ppt translator mvp"
```
