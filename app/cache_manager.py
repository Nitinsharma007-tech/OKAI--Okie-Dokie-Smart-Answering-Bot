import json
import time
from pathlib import Path

import faiss
import numpy as np


class CacheManager:
    """
    Semantic cache for question / answer pairs.

    Predefined or previously-generated Q&A pairs are stored in a JSON file
    along with their embeddings. When a new question arrives, it is
    embedded and compared against every cached question using cosine
    similarity (FAISS inner-product search on normalized vectors).

    If the best match's similarity >= `threshold`, the cached answer is
    returned directly, so no Gemini API call is made. Otherwise the
    caller falls back to search + Gemini, and the new pair can be added
    to the cache via `add()` so it is served from cache next time.
    """

    def __init__(
        self,
        embed_fn,
        cache_file="data/cache/qa_cache.json",
        lookup_threshold=0.93,
        duplicate_threshold=0.98,
    ):

        self.embed_fn = embed_fn

        cache_path = Path(cache_file)

        if not cache_path.is_absolute():
            # Resolve relative to the project root (two levels up from
            # this file, same convention used by semantic_search.py and
            # knowledge_browser.py), instead of the process's cwd.
            BASE_DIR = Path(__file__).resolve().parent.parent
            cache_path = BASE_DIR / cache_path

        self.cache_file = cache_path

        self.lookup_threshold = lookup_threshold
        self.duplicate_threshold = duplicate_threshold

        self.entries = []
        self.index = None
        self.dim = None

        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        self.load()

    # =====================================================
    # Load Cache From Disk
    # =====================================================

    def load(self):

        if self.cache_file.exists():

            with open(self.cache_file, "r", encoding="utf-8") as f:
                self.entries = json.load(f)

        else:
            self.entries = []

        # Compute embeddings for any predefined entries that don't have
        # one yet (e.g. you hand-wrote {"question":..., "answer":...})

        updated = False

        for entry in self.entries:

            if "embedding" not in entry or not entry["embedding"]:
                entry["embedding"] = self.embed_fn(entry["question"]).tolist()
                updated = True

        if updated:
            self.save()

        self._build_index()

        print("=" * 60)
        print(
            f"QA Cache Loaded ({len(self.entries)} entries)"
        )
        print(
            f"Lookup Threshold    : {self.lookup_threshold}"
        )
        print(
            f"Duplicate Threshold : {self.duplicate_threshold}"
        )
        print("=" * 60)

    # =====================================================
    # Save Cache To Disk
    # =====================================================

    def save(self):

        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

    # =====================================================
    # Build FAISS Index From Cached Embeddings
    # =====================================================

    def _build_index(self):

        if not self.entries:
            self.index = None
            return

        vectors = np.array(
            [e["embedding"] for e in self.entries],
            dtype=np.float32,
        )

        self.dim = vectors.shape[1]

        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(vectors)

    # =====================================================
    # Look Up A Question In The Cache
    # =====================================================

    def lookup(self, question):
        """
        Returns {"question", "answer", "score"} on a cache HIT,
        or None on a MISS (caller should fall back to search + Gemini).
        """

        if self.index is None or self.index.ntotal == 0:
            print("=" * 60)
            print("CACHE LOOKUP SKIPPED — index is empty")
            print(f"Cache file checked : {self.cache_file}")
            print(f"Cache file exists?  : {self.cache_file.exists()}")
            print("=" * 60)
            return None

        embedding = self.embed_fn(question)
        print("=" * 60)
        print("CACHE LOOKUP")
        print(f"Question : {question}")
        print(f"Total Cache Entries : {len(self.entries)}")
        print("=" * 60)
        scores, indices = self.index.search(
            np.array([embedding], dtype=np.float32),
            1,
        )

        best_score = float(scores[0][0])
        print(f"Best Cache Similarity : {best_score:.4f}")
        print(f"Threshold             : {self.lookup_threshold}")
        best_idx = int(indices[0][0])

        if best_idx == -1:
            return None

        if best_score >= self.lookup_threshold:

            entry = self.entries[best_idx]

            print("=" * 60)
            print("✅ CACHE HIT")
            print(f"Similarity : {best_score:.4f}")
            print(f"Source     : {entry.get('source', 'unknown')}")
            print("=" * 60)

            return {
                "question": entry["question"],
                "answer": entry["answer"],
                "score": round(best_score, 4),
                "source": entry.get("source", "unknown"),
            }

        print(f"❌ Cache MISS (best similarity={best_score:.4f})")

        return None

    # =====================================================
    # Add A New Q&A Pair To The Cache (e.g. after a fresh
    # Gemini call), so it is served from cache next time
    # =====================================================

    def add(self, question, answer, source="dynamic"):

        if self.is_duplicate(question):

            print("⚠ Duplicate question. Skipping cache save.")

            return

        embedding = self.embed_fn(question)

        entry = {

            "id": len(self.entries) + 1,

            "question": question,

            "answer": answer,

            "source": source,

            "embedding": embedding.tolist(),

            "created_at": time.time()

        }

        self.entries.append(entry)

        if self.index is None:
            self._build_index()

        else:
            self.index.add(
                np.array([embedding], dtype=np.float32)
            )

        self.save()

        print("✅ Added to semantic cache.")

    # =====================================================
    # Bulk-Seed With Predefined Q&A Pairs
    # (embeddings are computed automatically)
    # =====================================================

    def add_predefined(self, qa_pairs):
        """
        qa_pairs : list of {"question": "...", "answer": "..."}
        """

        for pair in qa_pairs:

            embedding = self.embed_fn(pair["question"])

            entry = {
                "id": len(self.entries) + 1,
                "question": pair["question"],
                "answer": pair["answer"],
                "source": pair.get("source", "manual"),
                "embedding": embedding.tolist(),
                "created_at": time.time(),
            }

            self.entries.append(entry)

        self._build_index()
        self.save()

    def seed_from_knowledge(self, knowledge_file="master_data/knowledge_master.json"):

        knowledge_file = Path(knowledge_file)

        if not knowledge_file.exists():
            print("Knowledge master not found.")
            return

        with open(knowledge_file, "r", encoding="utf-8") as f:
            knowledge = json.load(f)

        topics = knowledge.get("topics", [])

        print("=" * 60)
        print(f"Generating Cache from {len(topics)} topics...")
        print("=" * 60)

        self.entries = []

        cache_id = 1

        for topic in topics:

            questions = topic.get("questions", [])

            answer_parts = []

            # Summary
            if topic.get("summary"):
                answer_parts.append(topic["summary"])

            # Steps
            if topic.get("steps"):
                answer_parts.append("\nSteps:")
                for i, step in enumerate(topic["steps"], start=1):
                    answer_parts.append(f"{i}. {step}")

            # Business Rules
            if topic.get("business_rules"):
                answer_parts.append("\nBusiness Rules:")
                for rule in topic["business_rules"]:
                    answer_parts.append(f"• {rule}")

            # Important Notes
            if topic.get("important_notes"):
                answer_parts.append("\nImportant Notes:")
                for note in topic["important_notes"]:
                    answer_parts.append(f"• {note}")

            answer = "\n".join(answer_parts)

            for question in questions:

                embedding = self.embed_fn(question)

                self.entries.append({
                    "id": cache_id,
                    "question": question,
                    "answer": answer,
                    "source": "knowledge",
                    "embedding": embedding.tolist(),
                    "created_at": time.time()
                })

                cache_id += 1

        self.save()
        self._build_index()

        print("=" * 60)
        print(f"Cache Created Successfully")
        print(f"Total Cached Questions : {len(self.entries)}")
        print("=" * 60)
    # =====================================================
    # Duplicate Check
    # =====================================================

    def is_duplicate(self, question):

        if self.index is None or self.index.ntotal == 0:
            return False

        embedding = self.embed_fn(question)

        scores, indices = self.index.search(
            np.array([embedding], dtype=np.float32),
            1,
        )

        best_score = float(scores[0][0])

        return best_score >= self.duplicate_threshold

if __name__ == "__main__":

    from app.semantic_search import SemanticSearch

    search = SemanticSearch()

    cache = CacheManager(
        embed_fn=search.embed_question
    )

    cache.seed_from_knowledge()