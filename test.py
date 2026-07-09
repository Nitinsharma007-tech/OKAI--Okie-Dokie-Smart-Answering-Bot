from app.Data_pipelining.knowledge_loader_embedding import KnowledgeLoader


def main():

    loader = KnowledgeLoader()

    loader.load()

    loader.show_info()


if __name__ == "__main__":
    main()