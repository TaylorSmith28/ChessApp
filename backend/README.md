```bash
python3 -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

```bash
.\.venv\Scripts\python -m uvicorn backend.app.main:app --port 8000
```