import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.pipeline.embedding_generator import EmbeddingGenerator


def main():

    generator = EmbeddingGenerator()

    generator.generate()


if __name__ == "__main__":
    main()
    