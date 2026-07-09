import os

from app.Data_pipelining.knowledge_generator import KnowledgeGenerator


def main():

    generator = KnowledgeGenerator()

    folder = "data/cleaned_transcripts"

    files = sorted([

        file

        for file in os.listdir(folder)

        if file.endswith(".txt")

    ])

    if not files:

        print("No cleaned transcripts found.")

        return

    print("=" * 60)
    print("OKAI - Knowledge Generator")
    print("=" * 60)

    print(f"\nFound {len(files)} cleaned transcript(s).\n")

    for i, file in enumerate(
        files,
        start=1
    ):

        print("-" * 60)
        print(f"[{i}/{len(files)}] {file}")
        print("-" * 60)

        generator.process_file(file)

    print("\n")
    print("=" * 60)
    print("Knowledge Base Generated Successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()