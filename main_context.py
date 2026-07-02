from app.semantic_search import SemanticSearch
from app.context_builder import ContextBuilder


def main():

    search = SemanticSearch()

    builder = ContextBuilder()

    while True:

        print("\n" + "=" * 60)

        question = input("Ask OKAI : ")

        if question.lower() in ["exit", "quit", "0"]:

            break

        results = search.search(question)

        context = builder.build(results)

        print("\n")
        print("=" * 80)
        print("CONTEXT SENT TO GEMINI")
        print("=" * 80)

        print(context)


if __name__ == "__main__":
    main()