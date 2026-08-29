import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.pipeline.transcript import TranscriptGenerator


def get_video_files(video_folder):
    return sorted([
        f for f in os.listdir(video_folder)
        if f.lower().endswith((".mp4", ".mkv", ".avi", ".mov"))
    ])


def get_pending_videos(video_folder, transcript_folder, force_reprocess=False):
    videos = get_video_files(video_folder)

    if force_reprocess:
        return videos

    pending_videos = []

    for video in videos:
        filename = os.path.splitext(video)[0]
        json_file = os.path.join(transcript_folder, filename + ".json")

        if not os.path.exists(json_file):
            pending_videos.append(video)

    return pending_videos


def main():
    parser = argparse.ArgumentParser(description="Generate speech transcripts for videos.")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Show the old manual selection menu instead of processing all videos automatically."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocess every video, even if a transcript JSON already exists."
    )
    args = parser.parse_args()

    generator = TranscriptGenerator(
        model_size="medium",
        device="cuda",
        compute_type="float16"
    )

    video_folder = "data/videos"
    transcript_folder = "data/transcripts/json"

    os.makedirs(transcript_folder, exist_ok=True)

    videos = get_video_files(video_folder)

    if not videos:
        print("No supported video files found in data/videos.")
        return

    if args.interactive:
        while True:
            pending_videos = get_pending_videos(video_folder, transcript_folder, force_reprocess=args.force)

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
        return

    pending_videos = get_pending_videos(video_folder, transcript_folder, force_reprocess=args.force)

    if not pending_videos:
        print("\nAll videos have already been transcribed.")
        return

    print("\n" + "=" * 60)
    print("        OKAI - Full Transcript Generator")
    print("=" * 60)
    print(f"Total videos found: {len(videos)}")
    print(f"Processing: {len(pending_videos)} videos")
    print("=" * 60)

    for video in pending_videos:
        generator.generate(video)

    print("\n" + "=" * 60)
    print("All videos processed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()