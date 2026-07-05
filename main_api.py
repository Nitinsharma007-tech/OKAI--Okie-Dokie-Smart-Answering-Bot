import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.chatbot import OKAIChatbot


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


@app.post("/api/ask")
def ask(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    bot = app.state.bot

    try:
        search_results = bot.search.search(question, top_k=3)
        context = bot.builder.build(search_results)

        prompt = f"""
You are OKAI, an intelligent ERP Assistant.

Answer ONLY using the knowledge provided below.

If the answer is not present in the knowledge,
say:

"I couldn't find this information in the ERP knowledge base."

Do not invent information.

Always answer professionally.

Always explain in simple language.

If there are steps,
present them as numbered points.

==========================
USER QUESTION
==========================

{question}

==========================
ERP KNOWLEDGE
==========================

{context}
"""

        answer = bot.gemini.generate(prompt)

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
            "knowledge": knowledge,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main_api:app", host="0.0.0.0", port=8000)
