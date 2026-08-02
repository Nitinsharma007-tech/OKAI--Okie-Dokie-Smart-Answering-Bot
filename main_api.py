import sys
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.chatbot import OKAIChatbot
from app.knowledge_browser import KnowledgeBrowser


class AskRequest(BaseModel):
    question: str


ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"

app = FastAPI(
    title="OKAI ERP Assistant API",
    description="Backend API for OKAI with JavaScript frontend.",
    version="1.0.0",
)

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

        return {
            "question": question,
            "answer": answer,
            "fromCache": from_cache,
            "knowledge": knowledge,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main_api:app", host="0.0.0.0", port=8000)
