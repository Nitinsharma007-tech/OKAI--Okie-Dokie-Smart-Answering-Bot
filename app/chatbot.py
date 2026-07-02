from app.semantic_search import SemanticSearch
from app.context_builder import ContextBuilder
from app.gemini_agent import GeminiAgent


class OKAIChatbot:

    def __init__(self):

        print("=" * 70)
        print("Initializing OKAI ERP Assistant...")
        print("=" * 70)

        self.search = SemanticSearch()

        self.builder = ContextBuilder()

        self.gemini = GeminiAgent()

        print("\nOKAI Ready!\n")

    # ======================================================
    # Ask
    # ======================================================

    def ask(self, question):

        print("\nSearching Knowledge Base...\n")

        search_results = self.search.search(
            question,
            top_k=3
        )

        context = self.builder.build(
            search_results
        )

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

        answer = self.gemini.generate(prompt)

        return answer