import time

from app.semantic_search import SemanticSearch
from app.context_builder import ContextBuilder
from app.gemini_agent import GeminiAgent
from app.cache_manager import CacheManager


class CacheGenerator:
    """
    Fully regenerates the semantic QA cache (data/cache/qa_cache.json).

    Two kinds of cache entries are handled differently:

    1. Knowledge-seeded entries (source == "knowledge", or missing
       "source" from an older seed run) — these are assembled
       deterministically from master_data/knowledge_master.json and
       never touched Gemini. Rebuilding them is free/instant via
       CacheManager.seed_from_knowledge().

    2. Dynamic entries (source == "dynamic") — these are answers that
       were actually written by Gemini during a live chat. These are
       re-asked through the current search + context + prompt pipeline
       so stale wording gets replaced with freshly generated text,
       not just find/replaced.
    """

    def __init__(self):

        print("=" * 60)
        print("Initializing Cache Generator...")
        print("=" * 60)

        self.search = SemanticSearch()
        self.builder = ContextBuilder()
        self.gemini = GeminiAgent()

        self.cache = CacheManager(
            embed_fn=self.search.embed_question,
            cache_file="data/cache/qa_cache.json",
            lookup_threshold=0.83,
            duplicate_threshold=0.98,
        )

    # =====================================================
    # Prompt Template (kept in sync with app/chatbot.py)
    # =====================================================

    def build_prompt(self, question, context):

        return f"""
    You are OD, an intelligent ERP Assistant for OD ERP.

    Answer ONLY using the knowledge provided.

    If the answer is not available inside the knowledge,
    say:

    "I couldn't find this information in the ERP knowledge base."

    Never invent information.

    Always explain clearly.

    If there are steps,
    show them as numbered points.

    =========================
    USER QUESTION
    =========================

    {question}

    =========================
    ERP KNOWLEDGE
    =========================

    {context}
    """

    # =====================================================
    # Step 1 — Reseed Knowledge-Based Entries (free, instant)
    # =====================================================

    def reseed_knowledge_entries(self):

        print("=" * 60)
        print("Reseeding knowledge-based cache entries...")
        print("=" * 60)

        self.cache.seed_from_knowledge()

        print(f"✅ Reseeded {len(self.cache.entries)} knowledge entries.")

    # =====================================================
    # Step 2 — Regenerate Dynamic Entries Through Gemini
    # =====================================================

    def regenerate_dynamic_entries(self, dynamic_entries):
        """
        dynamic_entries : list of previously-saved dynamic entries
        (pulled out BEFORE reseed_knowledge_entries() wipes the cache).

        NOTE: we intentionally do NOT use cache.add() here — it runs a
        duplicate check that would silently skip a question whose
        embedding is >= duplicate_threshold similar to a freshly
        reseeded knowledge entry (very likely, since dynamic questions
        often closely match knowledge topics). We want to force these
        back into the cache regardless.
        """

        print("=" * 60)
        print(f"Regenerating {len(dynamic_entries)} dynamic entries via Gemini...")
        print("=" * 60)

        for i, entry in enumerate(dynamic_entries, start=1):

            question = entry["question"]

            print(f"[{i}/{len(dynamic_entries)}] Regenerating: {question}")

            results = self.search.search(question, top_k=3)
            context = self.builder.build(results)
            prompt = self.build_prompt(question, context)

            try:
                answer = self.gemini.generate(prompt)

            except Exception as e:

                print(f"  ⚠ Gemini call failed, keeping previous answer. Error: {e}")
                answer = entry["answer"]

            embedding = self.search.embed_question(question)

            self.cache.entries.append({
                "id": len(self.cache.entries) + 1,
                "question": question,
                "answer": answer,
                "source": "dynamic",
                "embedding": embedding.tolist(),
                "created_at": time.time(),
            })

            time.sleep(1)  # be gentle on the API

        self.cache._build_index()
        self.cache.save()

        print("✅ Dynamic entries regenerated and saved.")

    # =====================================================
    # Run Full Regeneration
    # =====================================================

    def run(self):

        dynamic_entries = [
            e for e in self.cache.entries if e.get("source") == "dynamic"
        ]

        print(f"Knowledge entries found : {len(self.cache.entries) - len(dynamic_entries)}")
        print(f"Dynamic entries found   : {len(dynamic_entries)}")

        self.reseed_knowledge_entries()

        if dynamic_entries:
            self.regenerate_dynamic_entries(dynamic_entries)
        else:
            print("No dynamic entries to regenerate.")

        print("=" * 60)
        print(f"🎉 Cache regeneration complete. Total entries: {len(self.cache.entries)}")
        print("=" * 60)