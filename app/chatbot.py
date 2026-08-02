from app.semantic_search import SemanticSearch
from app.context_builder import ContextBuilder
from app.gemini_agent import GeminiAgent
from app.cache_manager import CacheManager
import time

class OKAIChatbot:

    def __init__(self):

        print("=" * 70)
        print("Initializing OKAI ERP Assistant...")
        print("=" * 70)

        self.search = SemanticSearch()

        self.builder = ContextBuilder()

        self.gemini = GeminiAgent()

        # Semantic Q&A cache — reuses the same embedding model as
        # SemanticSearch, so no extra model load / dependency.

        self.cache = CacheManager(
        embed_fn=self.search.embed_question,
        cache_file="data/cache/qa_cache.json",
        lookup_threshold=0.83,
        duplicate_threshold=0.98,
    )

        print("\nOKAI Ready!\n")

    # ======================================================
    # Ask
    # ======================================================
    def ask(self, question):

        # --------------------------------------------------
        # 0. Embed once, reuse everywhere
        # --------------------------------------------------

        t_embed = time.time()
        question_embedding = self.search.embed_question(question)
        print(f"[TIMING] embed_question: {time.time()-t_embed:.2f}s")

        # --------------------------------------------------
        # 1. Try Cache First
        # --------------------------------------------------

        print("\n========== CHECKING CACHE ==========")

        t0 = time.time()
        cached = self.cache.lookup(question, embedding=question_embedding)
        print(f"[TIMING] cache.lookup: {time.time()-t0:.2f}s")

        if cached:
            print("✅ CACHE HIT - Returning cached answer")
            return cached["answer"], None, True

        print("❌ CACHE MISS - Calling Semantic Search + Gemini")

        # --------------------------------------------------
        # 2. Cache Miss -> Semantic Search + Gemini
        # --------------------------------------------------

        print("\nSearching Knowledge Base...\n")

        t1 = time.time()
        search_results = self.search.search(
            question,
            top_k=3,
            embedding=question_embedding
        )
        print(f"[TIMING] search: {time.time()-t1:.2f}s")

        t2 = time.time()
        context = self.builder.build(search_results)
        print(f"[TIMING] context build: {time.time()-t2:.2f}s")

        prompt = f"""
    You are OKAI, an intelligent ERP Assistant.

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

        t3 = time.time()
        answer = self.gemini.generate(prompt)
        print(f"[TIMING] gemini.generate: {time.time()-t3:.2f}s")

        # Save only meaningful answers
        if answer:

            invalid_responses = [
                "I couldn't find this information",
                "I could not find this information",
                "not available in the ERP knowledge base"
            ]

            if not any(text.lower() in answer.lower() for text in invalid_responses):

                print("\n💾 Saving response to semantic cache...")

                self.cache.add(
                    question,
                    answer,
                    source="dynamic"
                )

        return answer, search_results, False
    