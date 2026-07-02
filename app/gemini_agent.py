import os
import json

from dotenv import load_dotenv
from google import genai


class GeminiAgent:

    def __init__(self):

        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found.")

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-2.5-flash"

        print("=" * 60)
        print("Gemini Agent Ready")
        print("=" * 60)

    def generate_json(
        self,
        system_prompt,
        user_prompt
    ):

        response = self.client.models.generate_content(
            model=self.model,
            contents=f"""
{system_prompt}

--------------------------

{user_prompt}
""",
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        )

        return json.loads(response.text)
        # =====================================================
    # Chat Response
    # =====================================================

    def generate(self, prompt):

        response = self.client.models.generate_content(

            model=self.model,

            contents=prompt,

            config={

                "temperature": 0.2

            }

        )

        return response.text