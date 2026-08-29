import os
import json

from dotenv import load_dotenv
from google import genai


class GeminiAgent:

    def __init__(self):

        load_dotenv()

        configured_keys = []
        for index in range(1, 6):
            key = os.getenv(f"GEMINI_API_KEY_{index}")
            if key:
                configured_keys.append(key)

        fallback_key = os.getenv("GEMINI_API_KEY")
        if fallback_key and fallback_key not in configured_keys:
            configured_keys.insert(0, fallback_key)

        self.api_keys = configured_keys

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

        for i, api_key in enumerate(self.api_keys, start=1):

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

                print(f"✅ JSON Success using API Key {i}")

                return json.loads(response.text)

            except Exception as e:

                print(f"❌ API Key {i} Failed")

                last_error = e

        raise last_error

    # =====================================================
    # Chat Response
    # =====================================================

    def generate(self, prompt):

        last_error = None

        for i, api_key in enumerate(self.api_keys, start=1):

            try:

                client = genai.Client(api_key=api_key)

                response = client.models.generate_content(

                    model=self.model,

                    contents=prompt,

                    config={
                        "temperature": 0.2
                    }

                )

                print(f"✅ Chat Success using API Key {i}")

                return response.text

            except Exception as e:

                print(f"❌ API Key {i} Failed")

                last_error = e

        raise last_error