import json
import faiss
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticSearch:

    def __init__(self):

        BASE_DIR = Path(__file__).resolve().parent.parent

        self.index_file = (
            BASE_DIR
            / "data"
            / "embeddings"
            / "knowledge.faiss"
        )

        self.records_file = (
            BASE_DIR
            / "data"
            / "embeddings"
            / "embedding_records.json"
        )

        print("=" * 60)
        print("Loading Semantic Search Engine...")
        print("=" * 60)

        # ----------------------------
        # Load Sentence Transformer
        # ----------------------------

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        print("Embedding Model Loaded")

        # ----------------------------
        # Load Embeddings
        # ----------------------------

        # ----------------------------
        # Load FAISS Index
        # ----------------------------

        if not self.index_file.exists():

            raise FileNotFoundError(

                f"\nFAISS Index not found:\n"

                f"{self.index_file}"

            )

        if not self.records_file.exists():

            raise FileNotFoundError(

                f"\nEmbedding records not found:\n"

                f"{self.records_file}"

            )

        self.index = faiss.read_index(

            str(self.index_file)

        )

        with open(

            self.records_file,

            "r",

            encoding="utf-8"

        ) as f:

            self.records = json.load(f)

        print(

            f"Embedding Records : {len(self.records)}"

        )

        print(

            f"FAISS Vectors : {self.index.ntotal}"

        )

        print("=" * 60)

        print("Semantic Search Ready")

        print("=" * 60)

    # =====================================================
    # Convert Question → Embedding
    # =====================================================

    def embed_question(self, question):

        embedding = self.model.encode(

            question,

            convert_to_numpy=True,

            normalize_embeddings=True

        )

        return embedding

    
    # =====================================================
    # Semantic Search
    # =====================================================

    def search(

        self,

        question,

        top_k=3

    ):

        print("\n" + "=" * 60)
        print("Semantic Search")
        print("=" * 60)

        print(f"Question : {question}\n")

        # ----------------------------------------
        # Question Embedding
        # ----------------------------------------

        question_embedding = self.embed_question(
            question
        )

        # ----------------------------------------
        # FAISS Search
        # ----------------------------------------

        scores, indices = self.index.search(

            np.array(
                [question_embedding],
                dtype=np.float32
            ),

            top_k

        )

        best_indices = indices[0]

        similarities = scores[0]

        results = []

        print("Top Matches")
        print("-" * 60)

        for rank, (index, score) in enumerate(
            zip(best_indices, similarities),
            start=1
        ):

            if index == -1:
                continue

            topic = self.records[index]

            print(
                f"{rank}. "
                f"{topic['topic']} "
                f"({score:.4f})"
            )

            results.append({

                "rank": rank,

                "score": round(float(score), 4),

                "topic_data": topic

            })
    
        print("-" * 60)

        return results

    # =====================================================
    # Pretty Print Results
    # =====================================================

    def show_results(

        self,

        results

    ):

        print("\n")

        for result in results:

            topic = result["topic_data"]

            print("=" * 60)

            print(

                f"Rank : "

                f"{result['rank']}"

            )

            print(

                f"Similarity : "

                f"{result['score']}"

            )

            print(

                f"Module : "

                f"{topic.get('module')}"

            )

            print(

                f"Topic : "

                f"{topic.get('topic')}"

            )

            print()

            print("Summary")

            print(topic.get("summary"))

            print()

            print("Navigation")

            for nav in topic.get(

                "navigation",

                []

            ):

                print(f"• {nav}")

            print()

            print("=" * 60)
    # =====================================================
    # Get Best Match
    # =====================================================

    def get_best_match(self, question):

        results = self.search(question, top_k=1)

        if len(results) == 0:
            return None

        return results[0]
    # =====================================================
    # Search By Module
    # =====================================================

    def search_module(self, question, module_name, top_k=5):

        question_embedding = self.embed_question(question)

        scores, indices = self.index.search(

            np.array(
                [question_embedding],
                dtype=np.float32
            ),

            len(self.records)

        )

        filtered = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            topic = self.records[idx]

            if topic.get("module", "").lower() == module_name.lower():

                filtered.append({

                    "score": float(score),

                    "topic": topic

                })

        results = []

        for rank, item in enumerate(filtered[:top_k], start=1):

            results.append({

                "rank": rank,

                "score": round(item["score"], 4),

                "topic_data": item["topic"]

            })

        return results

    # =====================================================
    # Display Search Results
    # =====================================================

    def display(self, results):

        print("\n")
        print("=" * 80)
        print("SEARCH RESULTS")
        print("=" * 80)

        for result in results:

            topic = result["topic_data"]

            print(f"\nRank       : {result['rank']}")
            print(f"Similarity : {result['score']}")
            print(f"Module     : {topic.get('module')}")
            print(f"Topic      : {topic.get('topic')}")

            print("\nSummary")
            print("-" * 40)
            print(topic.get("summary", ""))

            if topic.get("navigation"):

                print("\nNavigation")
                print("-" * 40)

                for nav in topic["navigation"]:
                    print(f"• {nav}")

            if topic.get("steps"):

                print("\nSteps")
                print("-" * 40)

                for i, step in enumerate(topic["steps"], start=1):
                    print(f"{i}. {step}")

            if topic.get("business_rules"):

                print("\nBusiness Rules")
                print("-" * 40)

                for rule in topic["business_rules"]:
                    print(f"• {rule}")

            if topic.get("important_notes"):

                print("\nImportant Notes")
                print("-" * 40)

                for note in topic["important_notes"]:
                    print(f"• {note}")

            print("\n" + "=" * 80)