import pickle
import json
from pathlib import Path
from datetime import datetime

from sentence_transformers import SentenceTransformer

from app.knowledge_loader_embedding import KnowledgeLoader


class EmbeddingGenerator:

    def __init__(self):

        self.loader = KnowledgeLoader()

        print("=" * 60)
        print("Loading Embedding Model...")
        print("=" * 60)

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        print("Embedding Model Loaded\n")

        self.embedding_dir = Path("data/embeddings")

        self.embedding_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.embedding_file = (
            self.embedding_dir /
            "knowledge_embeddings.pkl"
        )

        self.metadata_file = (
            self.embedding_dir /
            "embedding_metadata.json"
        )

    # =====================================================
    # Create Search Text
    # =====================================================

    def build_search_text(self, topic):

        text = f"""
Module:
{topic.get("module","")}

Topic:
{topic.get("topic","")}

Summary:
{topic.get("summary","")}

Navigation:
{' | '.join(topic.get("navigation", []))}

Steps:
{' '.join(topic.get("steps", []))}

Business Rules:
{' '.join(topic.get("business_rules", []))}

Important Notes:
{' '.join(topic.get("important_notes", []))}

Questions:
{' '.join(topic.get("questions", []))}

Keywords:
{' '.join(topic.get("keywords", []))}

Related Topics:
{' '.join(topic.get("related_topics", []))}
"""

        return text.strip()

    # =====================================================
    # Generate Embeddings
    # =====================================================

    def generate(self):

        topics = self.loader.load()

        embeddings = []

        total = len(topics)

        print("\nGenerating Embeddings...\n")

        for i, topic in enumerate(topics, start=1):

            print(
                f"[{i}/{total}] "
                f"{topic['topic']}"
            )

            search_text = self.build_search_text(topic)

            vector = self.model.encode(
                search_text,
                normalize_embeddings=True
            )

            embeddings.append({

            "embedding": vector,

            "topic_data": topic

})

        # ----------------------------
        # Save Pickle
        # ----------------------------

        with open(
            self.embedding_file,
            "wb"
        ) as f:

            pickle.dump(
                embeddings,
                f
            )

        # ----------------------------
        # Save Metadata
        # ----------------------------

        metadata = {

            "project":
            "OKAI ERP",

            "model":
            "all-MiniLM-L6-v2",

            "dimension":
            len(embeddings[0]["embedding"]),

            "topics":
            len(embeddings),

            "generated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        }

        with open(
            self.metadata_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                metadata,
                f,
                indent=4
            )

        print("\n" + "=" * 60)
        print("Embedding Generation Completed")
        print("=" * 60)

        print(
            f"Topics Embedded : {len(embeddings)}"
        )

        print(
            f"Embedding Size : "
            f"{metadata['dimension']}"
        )

        print(
            f"Saved : {self.embedding_file}"
        )

        print(
            f"Saved : {self.metadata_file}"
        )