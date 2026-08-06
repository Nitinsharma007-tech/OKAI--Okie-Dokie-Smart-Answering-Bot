from app.pipeline.document_extracter import DocumentIngestor


def main():

    ingestor = DocumentIngestor()

    print("=" * 60)
    print("OD - Document Ingestor")
    print("=" * 60)

    ingestor.run()


if __name__ == "__main__":
    main()