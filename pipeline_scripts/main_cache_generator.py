from app.pipeline.cache_generator import CacheGenerator


def main():

    generator = CacheGenerator()

    print("=" * 60)
    print("OKAI - Cache Generator")
    print("=" * 60)

    generator.run()

    print("=" * 60)
    print("Cache regenerated successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()