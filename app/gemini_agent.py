import os
import json

from dotenv import load_dotenv
from google import genai


class GeminiAgent:

    def __init__(self):

        load_dotenv()

        self.api_keys = [

            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3")

        ]

        # Remove empty keys
        self.api_keys = [key for key in self.api_keys if key]

        if not self.api_keys:
            raise ValueError("No Gemini API Keys Found.")

        self.model = "gemini-2.5-flash"

        print("=" * 60)
        print(f"Gemini Agent Ready ({len(self.api_keys)} API Keys)")
        print("=" * 60)

    # =====================================================
    # JSON Generation
    # =====================================================

    def generate_json(self, system_prompt, user_prompt):

        prompt = f"""
{system_prompt}

--------------------------

{user_prompt}
"""

        last_error = None

        for i, api_key in enumerate(self.api_keys):

            try:

                client = genai.Client(api_key=api_key)

                response = client.models.generate_content(

                    model=self.model,

                    contents=prompt,

                    config={
                        "response_mime_type": "application/json",
                        "temperature": 0.2
                    }

                )

                print(f"✅ JSON Success using API Key {i+1}")

                return json.loads(response.text)

            except Exception as e:

                print(f"❌ API Key {i+1} Failed")

                last_error = e

        raise last_error

    # =====================================================
    # Chat Response
    # =====================================================

    def generate(self, prompt):

        last_error = None

        for i, api_key in enumerate(self.api_keys):

            try:

                client = genai.Client(api_key=api_key)

                response = client.models.generate_content(

                    model=self.model,

                    contents=prompt,

                    config={
                        "temperature": 0.2
                    }

                )

                print(f"✅ Chat Success using API Key {i+1}")

                return response.text

            except Exception as e:

                print(f"❌ API Key {i+1} Failed")

                last_error = e

        raise last_error