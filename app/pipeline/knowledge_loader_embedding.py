import json
from pathlib import Path


class KnowledgeLoader:

    def __init__(self):

        BASE_DIR = Path(__file__).resolve().parent.parent.parent

        self.master_file = (
            BASE_DIR
            / "master_data"
            / "knowledge_master.json"
        )

        self.master_data = {}

        self.topics = []

    # =====================================================
    # Load Master Knowledge
    # =====================================================

    def load(self):

        print("=" * 60)
        print("Loading Knowledge Master...")
        print("=" * 60)

        print("Looking For:")
        print(self.master_file)

        print("Exists:", self.master_file.exists())

        if not self.master_file.exists():

            raise FileNotFoundError(
                f"\nKnowledge Master not found:\n{self.master_file}"
            )

        with open(self.master_file, "r", encoding="utf-8") as f:

            self.master_data = json.load(f)

        self.topics = self.master_data.get("topics", [])

        print(f"\nTopics Loaded : {len(self.topics)}")

        return self.topics

    # =====================================================
    # Project Info
    # =====================================================

    def get_info(self):

        return {

            "project": self.master_data.get("project"),

            "version": self.master_data.get("version"),

            "modules": self.master_data.get("total_modules"),

            "topics": self.master_data.get("total_topics")

        }

    # =====================================================
    # Show Info
    # =====================================================

    def show_info(self):

        info = self.get_info()

        print("\nKnowledge Base Information")

        print("-" * 40)

        print(f"Project : {info['project']}")

        print(f"Version : {info['version']}")

        print(f"Modules : {info['modules']}")

        print(f"Topics  : {info['topics']}")

        print("-" * 40)