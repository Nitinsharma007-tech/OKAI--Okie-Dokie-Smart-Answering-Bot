from app.semantic_search import SemanticSearch


def main():

    search = SemanticSearch()

    while True:

        print("\n" + "=" * 60)

        question = input("Ask OKAI : ")

        if question.lower() in ["exit", "quit", "0"]:

            print("\nGoodbye!\n")

            break

        results = search.search(question, top_k=5)

        search.display(results)


if __name__ == "__main__":
    main()