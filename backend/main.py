import os
import hmac
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import requests
from fastapi import FastAPI, Depends, Header, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("HAGAI_DATA_DIR", APP_DIR / "data"))
UPLOAD_DIR = DATA_DIR / "datasets"
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "hagai.db"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
HAGAI_API_KEY = os.getenv("HAGAI_API_KEY", "")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".csv", ".jsonl"}

app = FastAPI(
    title="HAGAI AI CLOUD API",
    version="1.0.0",
    description="Private API gateway for HAGAI AI CLOUD and an Ollama model server."
)

origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

init_db()

def require_api_key(authorization: Optional[str] = Header(default=None)):
    if not HAGAI_API_KEY:
        raise HTTPException(status_code=503, detail="Backend haijasanidiwa: weka HAGAI_API_KEY kwenye environment.")
    expected = "Bearer " + HAGAI_API_KEY
    if not authorization or not hmac.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="API key si sahihi.")
    return True

def ollama_get(path: str):
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}{path}", timeout=8)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Ollama haipatikani: {exc}")

@app.get("/")
def root():
    return {"name": "HAGAI AI CLOUD API", "version": "1.0.0", "docs": "/docs"}

@app.get("/api/health")
def health():
    try:
        ollama_get("/api/tags")
        ollama_online = True
    except HTTPException:
        ollama_online = False
    return {"ok": True, "service": "HAGAI AI CLOUD", "ollama": ollama_online}

@app.get("/api/models")
def list_models(_: bool = Depends(require_api_key)):
    payload = ollama_get("/api/tags")
    models = []
    for item in payload.get("models", []):
        details = item.get("details") or {}
        size = int(item.get("size") or 0)
        models.append({
            "name": item.get("name", ""),
            "family": details.get("family", "unknown"),
            "parameter_size": details.get("parameter_size", ""),
            "quantization": details.get("quantization_level", ""),
            "size_bytes": size,
            "size_human": f"{size / (1024**3):.2f} GB" if size else "--",
            "modified_at": item.get("modified_at", "")
        })
    return {"models": models}

class ChatRequest(BaseModel):
    model: str = Field(min_length=1, max_length=160)
    message: str = Field(min_length=1, max_length=12000)
    system: Optional[str] = Field(default=None, max_length=4000)

@app.post("/api/chat")
def chat(body: ChatRequest, _: bool = Depends(require_api_key)):
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": body.model,
                "messages": ([{"role": "system", "content": body.system}] if body.system else [])
                           + [{"role": "user", "content": body.message}],
                "stream": False
            },
            timeout=(10, 300)
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Modeli haipo kwenye Ollama. Pakua kwanza kwenye Model Library.")
        response.raise_for_status()
        data = response.json()
        return {"model": body.model, "response": (data.get("message") or {}).get("content", "")}
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Ombi limechukua muda mrefu. Jaribu tena au tumia modeli ndogo.")
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Hitilafu ya Ollama: {exc}")

class PullRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160, pattern=r"^[A-Za-z0-9._:/-]+$")

@app.post("/api/models/pull")
def pull_model(body: PullRequest, _: bool = Depends(require_api_key)):
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/pull",
            json={"name": body.name, "stream": False},
            timeout=(10, 1800)
        )
        response.raise_for_status()
        return {"ok": True, "model": body.name, "result": response.json()}
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Upakuaji umechukua muda mrefu. Kagua hali ya Ollama na ujaribu tena.")
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Imeshindikana kupakua modeli: {exc}")

@app.get("/api/datasets")
def list_datasets(_: bool = Depends(require_api_key)):
    with db() as con:
        rows = con.execute("SELECT filename, size_bytes, created_at FROM datasets ORDER BY id DESC").fetchall()
    items = []
    for row in rows:
        size = row["size_bytes"]
        items.append({
            "filename": row["filename"],
            "size_bytes": size,
            "size_human": f"{size / 1024:.1f} KB",
            "created_at": row["created_at"]
        })
    return {"datasets": items}

@app.post("/api/datasets")
async def upload_dataset(file: UploadFile = File(...), _: bool = Depends(require_api_key)):
    original = Path(file.filename or "dataset").name
    suffix = Path(original).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Aina zinazoruhusiwa: TXT, CSV na JSONL.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Faili limezidi kikomo cha 10MB.")
    if not content:
        raise HTTPException(status_code=400, detail="Faili halina data.")
    safe_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}{suffix}"
    target = UPLOAD_DIR / safe_name
    target.write_bytes(content)
    created = datetime.now(timezone.utc).isoformat()
    with db() as con:
        con.execute(
            "INSERT INTO datasets(filename, stored_name, size_bytes, created_at) VALUES (?, ?, ?, ?)",
            (original, safe_name, len(content), created)
        )
    return {"ok": True, "filename": original, "size_bytes": len(content), "created_at": created}

@app.get("/api")
def api_index():
    return {"endpoints": ["/api/health", "/api/models", "/api/chat", "/api/models/pull", "/api/datasets"]}
