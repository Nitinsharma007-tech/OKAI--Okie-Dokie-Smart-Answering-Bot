import base64
import hashlib
import hmac
import json
import os
import sys
import threading
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.chatbot import OKAIChatbot
from app.knowledge_browser import KnowledgeBrowser
from app.pipeline.upload_pipeline import SUPPORTED_EXTENSIONS, get_pipeline_state, start_upload_pipeline


class AskRequest(BaseModel):
    question: str


class DataLoginRequest(BaseModel):
    username: str
    password: str


ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"
UPLOAD_DIR = ROOT_DIR / "data" / "manual_uploads"
TOKEN_TTL_SECONDS = 60 * 60

load_dotenv(ROOT_DIR / ".env")

app = FastAPI(
    title="OKAI ERP Assistant API",
    description="Backend API for OKAI with JavaScript frontend.",
    version="1.0.0",
)

_runtime_refresh_lock = threading.Lock()
_knowledge_tree_lock = threading.Lock()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    app.state.bot = OKAIChatbot()
    app.state.browser = KnowledgeBrowser()
    app.state.runtime_data_signature = _runtime_data_signature()


def _runtime_data_signature():
    files = (
        ROOT_DIR / "data" / "embeddings" / "knowledge.faiss",
        ROOT_DIR / "data" / "embeddings" / "embedding_records.json",
        ROOT_DIR / "data" / "cache" / "qa_cache.json",
        ROOT_DIR / "master_data" / "knowledge_master.json",
    )
    return tuple(file.stat().st_mtime_ns if file.exists() else 0 for file in files)


def _refresh_runtime_data_if_needed():
    current_signature = _runtime_data_signature()
    if current_signature == getattr(app.state, "runtime_data_signature", None):
        return

    if get_pipeline_state().get("status") == "running":
        return

    with _runtime_refresh_lock:
        if current_signature == getattr(app.state, "runtime_data_signature", None):
            return
        app.state.bot = OKAIChatbot()
        app.state.browser = KnowledgeBrowser()
        app.state.runtime_data_signature = _runtime_data_signature()

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "message": "OKAI API is running.",
    }


@app.get("/api/status")
def status():
    bot = app.state.bot
    return {
        "knowledgeTopics": len(bot.search.records),
        "topK": 3,
        "model": bot.gemini.model,
    }


def _token_signature(payload: str) -> str:
    secret = os.getenv("DATA_UPLOAD_SECRET")
    if not secret:
        raise RuntimeError("DATA_UPLOAD_SECRET is not configured.")
    digest = hmac.new(secret.encode("utf-8"), payload.encode("ascii"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _create_upload_token(username: str) -> str:
    payload = base64.urlsafe_b64encode(
        json.dumps(
            {"sub": username, "exp": int(time.time()) + TOKEN_TTL_SECONDS},
            separators=(",", ":"),
        ).encode("utf-8")
    ).decode("ascii").rstrip("=")
    return f"{payload}.{_token_signature(payload)}"


def require_upload_auth(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Upload authentication required.")

    try:
        payload, signature = authorization[7:].split(".", 1)
        if not hmac.compare_digest(signature, _token_signature(payload)):
            raise ValueError
        decoded = json.loads(base64.urlsafe_b64decode(payload + "=="))
        if int(decoded["exp"]) <= int(time.time()):
            raise ValueError
        return decoded["sub"]
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=401, detail="Invalid or expired upload token.")


@app.post("/api/data-login")
def data_login(request: DataLoginRequest):
    configured_username = os.getenv("DATA_UPLOAD_USERNAME")
    configured_password = os.getenv("DATA_UPLOAD_PASSWORD")
    if not configured_username or not configured_password or not os.getenv("DATA_UPLOAD_SECRET"):
        raise HTTPException(status_code=503, detail="Data upload authentication is not configured.")

    if not (
        hmac.compare_digest(request.username, configured_username)
        and hmac.compare_digest(request.password, configured_password)
    ):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    return {"access_token": _create_upload_token(request.username), "token_type": "bearer"}


@app.post("/api/data-upload")
async def data_upload(
    files: list[UploadFile] = File(...),
    username: str = Depends(require_upload_auth),
):
    del username
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    video_dir = ROOT_DIR / "data" / "videos"
    saved_files = []
    saved_paths = []
    for uploaded_file in files:
        filename = Path(uploaded_file.filename or "uploaded-file").name
        extension = Path(filename).suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension or 'unknown'}")
        destination_dir = video_dir if extension in {".mp4", ".mkv", ".avi", ".mov"} else UPLOAD_DIR
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / f"{uuid.uuid4().hex}_{filename}"
        destination.write_bytes(await uploaded_file.read())
        saved_files.append(filename)
        saved_paths.append(destination)
        await uploaded_file.close()

    start_upload_pipeline(saved_paths)
    return {
        "message": f"{len(saved_files)} file(s) uploaded. Knowledge pipeline started...",
        "files": saved_files,
        "status": "processing",
    }


@app.get("/api/data-status")
def data_status(username: str = Depends(require_upload_auth)):
    del username
    return get_pipeline_state()


@app.get("/api/modules")
def get_modules():

    browser = app.state.browser

    return browser.get_modules_with_stats()
@app.get("/api/module/{module_name}")
def get_module(module_name: str):

    browser = app.state.browser

    return browser.get_module_tree(module_name)
@app.get("/api/topic/{topic_id}")
def get_topic(topic_id: str):

    browser = app.state.browser

    topic = browser.get_topic(topic_id)

    if topic is None:

        raise HTTPException(
            status_code=404,
            detail="Topic not found."
        )

    return topic

@app.post("/api/ask")
def ask(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    _refresh_runtime_data_if_needed()
    bot = app.state.bot

    try:
        answer, search_results, from_cache = bot.ask(question)

        # bot.ask() skips search on a cache hit (that's what makes the
        # hit fast — no wasted work). But the frontend's middle panel
        # always wants a navigation/knowledge card to show, cache hit
        # or not, so we run search here when it's missing. This is a
        # cheap local FAISS lookup — the expensive part (the Gemini
        # call) is still fully skipped on a cache hit.
        if search_results is None:
            search_results = bot.search.search(question, top_k=3)

        knowledge = []
        for result in search_results:
            topic = result["topic_data"]
            knowledge.append(
                {
                    "rank": result["rank"],
                    "score": result["score"],
                    "topic": topic.get("topic"),
                    "module": topic.get("module"),
                    "summary": topic.get("summary"),
                    "navigation": topic.get("navigation", []),
                }
            )

        # A useful manual question is retained as a question under the best
        # semantic topic, making it discoverable from the tree on later visits.
        tree_addition = None
        answer_is_knowledge_based = answer and not any(
            phrase in answer.lower()
            for phrase in (
                "i couldn't find this information",
                "i could not find this information",
                "not available in the erp knowledge base",
            )
        )
        if answer_is_knowledge_based and search_results:
            best_topic_id = search_results[0]["topic_data"].get("id")
            if best_topic_id is not None:
                with _knowledge_tree_lock:
                    tree_addition = app.state.browser.add_question_to_topic(question, best_topic_id)
                    if tree_addition:
                        app.state.runtime_data_signature = _runtime_data_signature()

        return {
            "question": question,
            "answer": answer,
            "fromCache": from_cache,
            "knowledge": knowledge,
            "treeAddition": tree_addition,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main_api:app", host="0.0.0.0", port=8000)
