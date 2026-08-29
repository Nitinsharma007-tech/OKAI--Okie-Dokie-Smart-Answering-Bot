import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.pipeline.transcript_cleaner import TranscriptCleaner


def main():

    cleaner = TranscriptCleaner()

    transcript_folder = "data/transcripts/txt"

    files = [
        f for f in os.listdir(transcript_folder)
        if f.endswith(".txt")
    ]

    if not files:
        print("No transcript files found.")
        return

    print("=" * 60)
    print("OKAI - Transcript Cleaner")
    print("=" * 60)
    print(f"Found {len(files)} transcript(s).\n")

    for i, file in enumerate(files, start=1):

        print(f"[{i}/{len(files)}] Cleaning: {file}")

        cleaner.clean_file(file)

        print()

    print("=" * 60)
    print("All transcripts cleaned successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()