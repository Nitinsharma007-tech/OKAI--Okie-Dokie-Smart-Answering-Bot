import os
import json
import re

from app.gemini_agent import GeminiAgent


class KnowledgeGenerator:

    def __init__(self):

        self.agent = GeminiAgent()

        self.input_folder = "data/cleaned_transcripts"
        self.output_folder = "data/knowledge_base"

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

        self.system_prompt = """
You are an ERP Knowledge Engineer.

You are building the knowledge base for an ERP AI Assistant called OKAI.

Your task is to convert ERP training transcripts into structured knowledge.

IMPORTANT RULES

1. Read the transcript carefully.

2. Detect every independent ERP topic.

3. Each topic MUST become ONE JSON object.

4. Ignore greetings.

5. Ignore filler words.

6. Ignore repeated conversations.

7. Never invent information.

8. Preserve ERP menu names exactly.

9. Preserve navigation exactly.

10. Preserve business rules.

11. Preserve warnings.

12. Preserve field names.

13. Preserve configurations.

14. Generate realistic user questions.

15. Generate useful search keywords.

16. Generate related topics.

17. Return ONLY VALID JSON.

Return ONLY a JSON ARRAY.

Schema:

[
{
"module":"",
"topic":"",
"summary":"",
"navigation":[],
"steps":[],
"business_rules":[],
"important_notes":[],
"questions":[],
"keywords":[],
"related_topics":[]
}
]

DO NOT WRITE ANYTHING EXCEPT JSON.
"""

    def process_file(self, filename):

        file_path = os.path.join(
            self.input_folder,
            filename
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            transcript = f.read()

        print(f"\nGenerating Knowledge : {filename}")

        try:

            topics = self.agent.generate_json(
                self.system_prompt,
                transcript
            )

            self.save_topics(
                topics,
                filename
            )

        except Exception as e:

            print(f"Error : {filename}")

            print(e)

    def save_topics(
        self,
        topics,
        source_file
    ):

        if not isinstance(
            topics,
            list
        ):

            print("Gemini returned invalid JSON.")

            return

        for index, topic in enumerate(
            topics,
            start=1
        ):

            module = topic.get(
                "module",
                "General"
            ).strip()

            module_folder = os.path.join(
                self.output_folder,
                module
            )

            os.makedirs(
                module_folder,
                exist_ok=True
            )

            topic_name = topic.get(
                "topic",
                "Unknown Topic"
            ).strip()

            safe_filename = re.sub(
                r'[<>:"/\\\\|?*]',
                "",
                topic_name
            )

            safe_filename = safe_filename.replace(
                " ",
                "_"
            )

            module_id = re.sub(
                r'[^a-zA-Z0-9]+',
                "_",
                module.lower()
            ).strip("_")

            topic_id = re.sub(
                r'[^a-zA-Z0-9]+',
                "_",
                topic_name.lower()
            ).strip("_")

            topic["id"] = f"{module_id}_{topic_id}"

            topic["source"] = {

                "file": source_file,

                "generated_by": "Gemini 2.5 Flash",

                "version": "1.0"

            }

            output_path = os.path.join(

                module_folder,

                f"{index:03}_{safe_filename}.json"

            )

            with open(

                output_path,

                "w",

                encoding="utf-8"

            ) as f:

                json.dump(

                    topic,

                    f,

                    indent=4,

                    ensure_ascii=False

                )

            print(f"   ✓ {safe_filename}")