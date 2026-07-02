import os
import re


class TranscriptCleaner:

    def __init__(
        self,
        input_folder="data/transcripts/txt",
        output_folder="data/cleaned_transcripts"
    ):

        self.input_folder = input_folder
        self.output_folder = output_folder

        os.makedirs(output_folder, exist_ok=True)

        self.filler_words = [

            "okay",
            "ok",
            "haan",
            "yes",
            "right",
            "actually",
            "basically",
            "sir",
            "ma'am",
            "hmm",
            "hello",
            "thank you"

        ]

    def clean_file(self, filename):

        input_path = os.path.join(
            self.input_folder,
            filename
        )

        output_path = os.path.join(
            self.output_folder,
            filename
        )

        if not os.path.exists(input_path):
            print("Transcript not found.")
            return

        with open(
            input_path,
            "r",
            encoding="utf-8"
        ) as f:

            text = f.read()

        # lowercase copy for matching
        cleaned = text

        for word in self.filler_words:

            cleaned = re.sub(
                rf"\b{re.escape(word)}\b",
                "",
                cleaned,
                flags=re.IGNORECASE
            )

        # Remove repeated spaces
        cleaned = re.sub(r"[ ]+", " ", cleaned)

        # Remove empty lines
        cleaned = re.sub(r"\n\s*\n", "\n", cleaned)

        cleaned = cleaned.strip()

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(cleaned)

        print("=" * 60)
        print("Transcript Cleaned Successfully")
        print("=" * 60)
        print(output_path)