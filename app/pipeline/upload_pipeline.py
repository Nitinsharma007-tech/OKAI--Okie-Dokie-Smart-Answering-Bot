import json
import os
import threading
from pathlib import Path

from app.pipeline.cache_generator import CacheGenerator
from app.pipeline.document_extracter import DocumentIngestor
from app.pipeline.embedding_generator import EmbeddingGenerator
from app.pipeline.knowledge_generator import KnowledgeGenerator
from app.pipeline.knowledge_master import KnowledgeMasterBuilder
from app.pipeline.transcript import TranscriptGenerator
from app.pipeline.transcript_cleaner import TranscriptCleaner

DOCUMENT_EXTENSIONS = {".docx", ".pdf", ".pptx", ".txt"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}
SUPPORTED_EXTENSIONS = DOCUMENT_EXTENSIONS | VIDEO_EXTENSIONS

_pipeline_run_lock = threading.Lock()
_state_lock = threading.Lock()
_pipeline_state = {
    "status": "idle",
    "progress": 0,
    "message": "Waiting for upload...",
    "steps": [],
}


def _knowledge_summary():
    master_file = Path("master_data/knowledge_master.json")
    if not master_file.exists():
        return {"ids": set(), "modules": set(), "questions": 0}
    with master_file.open("r", encoding="utf-8") as file:
        topics = json.load(file).get("topics", [])
    return {
        "ids": {topic.get("id") for topic in topics if topic.get("id")},
        "modules": {topic.get("module") for topic in topics if topic.get("module")},
        "questions": sum(len(topic.get("questions", [])) for topic in topics),
    }


def _filename_summary(uploaded_paths):
    names = [Path(path).name for path in uploaded_paths if path]
    if not names:
        return "No files uploaded."
    if len(names) == 1:
        return names[0]
    return f"{', '.join(names[:-1])}, and {names[-1]}"


def _known_upload_names():
    names = set()

    processed_dir = Path("data/manual_uploads/processed")
    if processed_dir.exists():
        names.update(path.name for path in processed_dir.iterdir() if path.is_file())

    master_file = Path("master_data/knowledge_master.json")
    if master_file.exists():
        try:
            with master_file.open("r", encoding="utf-8") as file:
                master = json.load(file)
        except (json.JSONDecodeError, OSError):
            master = {"topics": []}

        for topic in master.get("topics", []):
            source = topic.get("source") or {}
            file_name = source.get("file")
            if file_name:
                names.add(Path(str(file_name)).name)

    return names


def _new_uploads(uploaded_paths):
    known_names = _known_upload_names()
    return [path for path in uploaded_paths if path and Path(path).name not in known_names]


def _repair_duplicate_questions():
    master_file = Path("master_data/knowledge_master.json")
    if not master_file.exists():
        return 0

    with master_file.open("r", encoding="utf-8") as file:
        master = json.load(file)

    seen_questions = set()
    removed = 0
    for topic in master.get("topics", []):
        unique_questions = []
        for question in topic.get("questions", []):
            normalized = " ".join(str(question).split()).lower()
            if not normalized or normalized in seen_questions:
                removed += 1
                continue
            seen_questions.add(normalized)
            unique_questions.append(question)
        topic["questions"] = unique_questions

    if removed:
        with master_file.open("w", encoding="utf-8") as file:
            json.dump(master, file, ensure_ascii=False, indent=2)
    return removed


def get_pipeline_state():
    with _state_lock:
        return dict(_pipeline_state, steps=list(_pipeline_state["steps"]))


def _update_state(status=None, progress=None, message=None, step=None):
    with _state_lock:
        if status is not None:
            _pipeline_state["status"] = status
        if progress is not None:
            _pipeline_state["progress"] = progress
        if message is not None:
            _pipeline_state["message"] = message
        if step:
            _pipeline_state["steps"].append(step)


def _run_step(name, progress, action):
    _update_state(progress=progress, message=f"Running {name}...", step={"name": name, "state": "running", "message": ""})
    action()
    with _state_lock:
        _pipeline_state["steps"][-1].update({"state": "done", "message": "Completed"})


def run_upload_pipeline(uploaded_paths):
    if not _pipeline_run_lock.acquire(blocking=False):
        return
    try:
        uploaded_paths = [path for path in uploaded_paths if path]
        new_uploads = _new_uploads(uploaded_paths)
        if not new_uploads:
            uploaded_summary = _filename_summary(uploaded_paths)
            _update_state(
                status="completed",
                progress=100,
                message=(
                    f"Uploaded: {uploaded_summary}. Already in the knowledge base. "
                    "No new modules, topics, or questions were added."
                ),
            )
            return

        repaired_duplicates = _repair_duplicate_questions()
        before = _knowledge_summary()
        _pipeline_state.update({"status": "running", "progress": 15, "message": "Starting knowledge pipeline...", "steps": []})
        document_paths = [path for path in new_uploads if Path(path).suffix.lower() in DOCUMENT_EXTENSIONS]
        video_paths = [path for path in new_uploads if Path(path).suffix.lower() in VIDEO_EXTENSIONS]

        if video_paths:
            video_names = [Path(path).name for path in video_paths]
            _run_step("Transcribe videos", 25, lambda: _transcribe_videos(video_names))
            _run_step("Clean transcripts", 40, lambda: _clean_new_transcripts(video_names))
            _run_step("Generate knowledge topics", 55, lambda: _generate_new_topics(video_names))
            _run_step("Build knowledge master", 68, lambda: KnowledgeMasterBuilder().build())

        if document_paths:
            _run_step("Extract uploaded documents", 72, lambda: DocumentIngestor().run())

        _run_step("Generate semantic embeddings", 86, lambda: EmbeddingGenerator().generate())
        _run_step("Regenerate answer cache", 96, lambda: CacheGenerator().run())
        after = _knowledge_summary()
        new_ids = after["ids"] - before["ids"]
        new_modules = after["modules"] - before["modules"]
        new_questions = after["questions"] - before["questions"]
        uploaded_summary = _filename_summary(uploaded_paths)
        if new_ids:
            message = (
                f"Uploaded: {uploaded_summary}. Added {len(new_modules)} module(s), {len(new_ids)} topic(s), "
                f"and {new_questions} question(s) to the knowledge base."
            )
        else:
            message = (
                f"Uploaded: {uploaded_summary}. Already in the knowledge base. "
                "No new modules, topics, or questions were added."
            )
        if repaired_duplicates:
            message += f" Skipped {repaired_duplicates} duplicate question(s)."
        _update_state(status="completed", progress=100, message=message)
    except Exception as exc:
        _update_state(status="failed", message=str(exc))
        with _state_lock:
            if _pipeline_state["steps"] and _pipeline_state["steps"][-1]["state"] == "running":
                _pipeline_state["steps"][-1].update({"state": "failed", "message": str(exc)})
    finally:
        _pipeline_run_lock.release()


def _transcribe_videos(video_names):
    generator = TranscriptGenerator(
        model_size=os.getenv("WHISPER_MODEL", "small"),
        device=os.getenv("WHISPER_DEVICE", "cpu"),
        compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
    )
    for video_name in video_names:
        generator.generate(video_name)


def _clean_new_transcripts(video_names):
    cleaner = TranscriptCleaner()
    transcript_folder = Path("data/transcripts/txt")
    for video_name in video_names:
        transcript_name = f"{Path(video_name).stem}.txt"
        if (transcript_folder / transcript_name).exists():
            cleaner.clean_file(transcript_name)


def _generate_new_topics(video_names):
    generator = KnowledgeGenerator()
    cleaned_folder = Path("data/cleaned_transcripts")
    for video_name in video_names:
        transcript_name = f"{Path(video_name).stem}.txt"
        if (cleaned_folder / transcript_name).exists():
            generator.process_file(transcript_name)


def start_upload_pipeline(uploaded_paths):
    thread = threading.Thread(target=run_upload_pipeline, args=(uploaded_paths,), daemon=True)
    thread.start()


__all__ = ["SUPPORTED_EXTENSIONS", "get_pipeline_state", "start_upload_pipeline"]
