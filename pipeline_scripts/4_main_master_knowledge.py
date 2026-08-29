import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.pipeline.knowledge_master import KnowledgeMasterBuilder


def main():

    builder = KnowledgeMasterBuilder()

    builder.build()


if __name__ == "__main__":
    main()