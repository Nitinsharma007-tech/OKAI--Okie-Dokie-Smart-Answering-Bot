import json
from pathlib import Path


class KnowledgeBrowser:

    def __init__(self):

        BASE_DIR = Path(__file__).resolve().parent.parent

        self.master_file = (
            BASE_DIR
            / "master_data"
            / "knowledge_master.json"
        )

        self.master_data = {}

        self.topics = []

        self.tree = {}

        self.load()

    # =====================================================
    # Load Knowledge
    # =====================================================

    def load(self):

        if not self.master_file.exists():

            raise FileNotFoundError(
                f"\nKnowledge Master not found:\n{self.master_file}"
            )

        with open(
            self.master_file,
            "r",
            encoding="utf-8"
        ) as f:

            self.master_data = json.load(f)

        self.topics = self.master_data.get(
            "topics",
            []
        )

        self.build_tree()

    # =====================================================
    # Build Tree
    # =====================================================

    def build_tree(self):

        self.tree = {}

        for topic in self.topics:

            module = topic.get(
                "module",
                "General"
            ).strip()

            if module not in self.tree:

                self.tree[module] = []

            self.tree[module].append(topic)

    # =====================================================
    # Modules
    # =====================================================

    def get_modules(self):

        return sorted(self.tree.keys())

    # =====================================================
    # Modules with Statistics
    # =====================================================

    def get_modules_with_stats(self):

        modules = []

        for module in self.get_modules():

            topics = self.tree[module]

            question_count = sum(
                len(t.get("questions", []))
                for t in topics
            )

            modules.append({

                "module": module,

                "topics": len(topics),

                "questions": question_count

            })

        return modules

    # =====================================================
    # Topics by Module
    # =====================================================

    def get_topics(self, module):

        if module not in self.tree:
            return []

        results = []

        for topic in self.tree[module]:

            results.append({

                "id": topic.get("id"),

                "topic": topic.get("topic"),

                "summary": topic.get("summary", ""),

                "question_count": len(
                    topic.get("questions", [])
                ),

                "questions": topic.get(
                    "questions",
                    []
                )

            })

        return results


    # =====================================================
    # Topic By ID
    # =====================================================

    def get_topic(self, topic_id):

        for topic in self.topics:

            if topic.get("id") == topic_id:

                return topic

        return None

    # =====================================================
    # Project Information
    # =====================================================

    def get_info(self):

        return {

            "project": self.master_data.get("project"),

            "version": self.master_data.get("version"),

            "modules": len(self.tree),

            "topics": len(self.topics),

            "questions": sum(

                len(t.get("questions", []))

                for t in self.topics

            )

        }
    def get_module_tree(self, module):

        if module not in self.tree:
            return []

        tree = []

        for topic in self.tree[module]:

            tree.append({

                "id": topic.get("id"),

                "topic": topic.get("topic"),

                "summary": topic.get("summary", ""),

                "question_count": len(
                    topic.get("questions", [])
                ),

                "questions": topic.get(
                    "questions",
                    []
                )

            })

        return tree