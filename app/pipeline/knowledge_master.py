import os
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class KnowledgeMasterBuilder:

    def __init__(self):

        # ==================================================
        # Paths
        # ==================================================

        self.input_folder = Path("data/knowledge_base")

        self.output_file = Path("master_data/knowledge_master.json")

        # ==================================================
        # Storage
        # ==================================================

        self.raw_topics = []

        self.cleaned_topics = []

        self.statistics = defaultdict(int)

        self.module_statistics = defaultdict(int)

        self.duplicates_removed = 0

        self.invalid_topics = 0

        # ==================================================
        # Required Fields
        # ==================================================

        self.required_fields = [

            "id",

            "module",

            "topic",

            "summary",

            "navigation",

            "steps",

            "business_rules",

            "important_notes",

            "questions",

            "keywords",

            "related_topics",

            "source"

        ]    # ==================================================
    # Load Every JSON
    # ==================================================

    def load_topics(self):

        print("=" * 60)
        print("Loading Knowledge JSON Files")
        print("=" * 60)

        total = 0

        if not self.input_folder.exists():

            print("Knowledge folder not found.")

            return

        for module in sorted(os.listdir(self.input_folder)):

            module_path = self.input_folder / module

            if not module_path.is_dir():
                continue

            print(f"\nModule : {module}")

            for file in sorted(module_path.glob("*.json")):

                try:

                    with open(
                        file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        topic = json.load(f)

                    topic["module_folder"] = module

                    topic["json_file"] = file.name

                    self.raw_topics.append(topic)

                    total += 1

                    print(f"   Loaded : {file.name}")

                except Exception as e:

                    print(f"   Failed : {file.name}")

                    print(e)

        print("\n")
        print("=" * 60)
        print(f"Total JSON Loaded : {total}")
        print("=" * 60)
            # ==================================================
    # Validate JSON
    # ==================================================

    def validate_topics(self):

        print("\nValidating Topics...\n")

        for topic in self.raw_topics:

            valid = True

            for field in self.required_fields:

                if field not in topic:

                    valid = False

                    print(
                        f"Missing '{field}' in "
                        f"{topic.get('topic','Unknown')}"
                    )

            if valid:

                self.cleaned_topics.append(topic)

            else:

                self.invalid_topics += 1

        print(
            f"Valid Topics : {len(self.cleaned_topics)}"
        )

        print(
            f"Invalid Topics : {self.invalid_topics}"
        )
            # ==================================================
    # Normalize Module Names
    # ==================================================

    def normalize_modules(self):

        print("\nNormalizing Module Names...\n")

        module_mapping = {

            "fee management": "Fees",
            "fees": "Fees",

            "transport management": "Transport",
            "transport": "Transport",

            "system": "System",
            "system setup": "System",
            "system configuration": "System",

            "hrm": "HRM",
            "inventory": "Inventory",
            "academics": "Academics",
            "procurement": "Procurement",
            "hostel management": "Hostel Management",
            "admission management": "Admission Management"

        }

        for topic in self.cleaned_topics:

            module = topic["module"].strip()

            normalized = module_mapping.get(
                module.lower(),
                module
            )

            topic["module"] = normalized

        print("Module normalization completed.")
            # ==================================================
    # Remove Duplicate Topics
    # ==================================================

    def remove_duplicates(self):

        print("\nRemoving Duplicate Topics...\n")

        unique_topics = {}

        for topic in self.cleaned_topics:

            key = (

                topic["module"].strip().lower(),

                topic["topic"].strip().lower()

            )

            if key not in unique_topics:

                unique_topics[key] = topic

            else:

                self.duplicates_removed += 1

        self.cleaned_topics = list(
            unique_topics.values()
        )

        print(
            f"Duplicates Removed : {self.duplicates_removed}"
        )

        print(
            f"Remaining Topics : {len(self.cleaned_topics)}"
        )
            # ==================================================
    # Sort Topics
    # ==================================================

    def sort_topics(self):

        print("\nSorting Topics...\n")

        self.cleaned_topics.sort(

            key=lambda topic: (

                topic["module"].lower(),

                topic["topic"].lower()

            )

        )

        print("Topics sorted.")
            # ==================================================
    # Generate Statistics
    # ==================================================

    def generate_statistics(self):

        print("\nGenerating Statistics...\n")

        self.statistics.clear()

        self.module_statistics.clear()

        self.statistics["total_topics"] = len(
            self.cleaned_topics
        )

        for topic in self.cleaned_topics:

            module = topic["module"]

            self.module_statistics[module] += 1

        self.statistics["total_modules"] = len(
            self.module_statistics
        )

        print(
            f"Modules : {self.statistics['total_modules']}"
        )

        print(
            f"Topics : {self.statistics['total_topics']}"
        )
            # ==================================================
    # Create Master JSON
    # ==================================================

    def create_master(self):

        print("\nCreating Master Knowledge Base...\n")

        module_list = []

        for module in sorted(self.module_statistics.keys()):

            module_list.append({

                "module": module,

                "topics": self.module_statistics[module]

            })

        master = {

            "project": "OKAI ERP Knowledge Base",

            "version": "1.0",

            "generated_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "total_modules": self.statistics[
                "total_modules"
            ],

            "total_topics": self.statistics[
                "total_topics"
            ],

            "duplicates_removed": self.duplicates_removed,

            "modules": module_list,

            "topics": self.cleaned_topics

        }

        return master
        # ==================================================
    # Save Master JSON
    # ==================================================

    def save_master(self, master):

        print("\nSaving Master Knowledge Base...\n")

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(

            self.output_file,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                master,

                f,

                indent=4,

                ensure_ascii=False

            )

        print("Knowledge Master Saved Successfully.")

        print(f"\nLocation : {self.output_file}")
            # ==================================================
    # Display Summary
    # ==================================================

    def display_summary(self):

        print("\n" + "=" * 60)

        print("Knowledge Master Summary")

        print("=" * 60)

        print(
            f"Modules : {self.statistics['total_modules']}"
        )

        print(
            f"Topics : {self.statistics['total_topics']}"
        )

        print(
            f"Duplicates Removed : {self.duplicates_removed}"
        )

        print(
            f"Invalid Topics : {self.invalid_topics}"
        )

        print("=" * 60)
            # ==================================================
    # Build Knowledge Master
    # ==================================================

    def build(self):

        print("\nStarting Knowledge Master Builder...\n")

        # Step 1
        self.load_topics()

        # Step 2
        self.validate_topics()

        # Step 3
        self.normalize_modules()

        # Step 4
        self.remove_duplicates()

        # Step 5
        self.sort_topics()

        # Step 6
        self.generate_statistics()

        # Step 7
        master = self.create_master()

        # Step 8
        self.save_master(master)

        # Step 9
        self.display_summary()

        print("\nKnowledge Master Build Completed.\n")