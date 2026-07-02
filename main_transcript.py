import os
from app.transcript import TranscriptGenerator


def main():

    # Load model only once
    generator = TranscriptGenerator(
        model_size="medium",
        device="cuda",
        compute_type="float16"
    )

    video_folder = "data/videos"
    transcript_folder = "data/transcripts/json"

    while True:

        videos = [
            f for f in os.listdir(video_folder)
            if f.lower().endswith((".mp4", ".mkv", ".avi", ".mov"))
        ]

        # Skip already processed videos
        pending_videos = []

        for video in videos:

            filename = os.path.splitext(video)[0]
            json_file = os.path.join(
                transcript_folder,
                filename + ".json"
            )

            if not os.path.exists(json_file):
                pending_videos.append(video)

        if not pending_videos:
            print("\nAll videos have already been transcribed.")
            break

        print("\n" + "=" * 60)
        print("          OKAI - Transcript Generator")
        print("=" * 60)

        for i, video in enumerate(pending_videos, start=1):
            print(f"{i}. {video}")

        print("0. Exit")

        try:

            choice = int(input("\nSelect a video: "))

            if choice == 0:
                print("\nExiting OKAI...")
                break

            if 1 <= choice <= len(pending_videos):
                generator.generate(pending_videos[choice - 1])
            else:
                print("Invalid Choice!")

        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    main()