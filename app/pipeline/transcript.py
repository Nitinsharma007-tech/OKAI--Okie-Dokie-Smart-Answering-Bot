import os
import json
import time
from datetime import datetime
from faster_whisper import WhisperModel
import traceback


class TranscriptGenerator:

    def __init__(
        self,
        video_folder="data/videos",
        output_folder="data/transcripts",
        model_size="medium",
        device="cuda",
        compute_type="float16"
    ):

        self.video_folder = video_folder
        self.output_folder = output_folder

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

        self.txt_folder = os.path.join(output_folder, "txt")
        self.json_folder = os.path.join(output_folder, "json")
        self.srt_folder = os.path.join(output_folder, "srt")
        self.metadata_folder = os.path.join(output_folder, "metadata")

        os.makedirs(self.txt_folder, exist_ok=True)
        os.makedirs(self.json_folder, exist_ok=True)
        os.makedirs(self.srt_folder, exist_ok=True)
        os.makedirs(self.metadata_folder, exist_ok=True)

        print("=" * 60)
        print(" Loading Faster-Whisper Model...")
        print("=" * 60)

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

        print(f" Model Loaded ({model_size})")
        print()

    def format_timestamp(self, seconds):

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)

        return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

    def generate(self, video_name):

        video_path = os.path.join(self.video_folder, video_name)

        if not os.path.exists(video_path):
            print(f" Video not found : {video_name}")
            return

        filename = os.path.splitext(video_name)[0]

        print("=" * 60)
        print(f" Processing : {video_name}")
        print("=" * 60)

        start_time = time.time()

        try:

            segments, info = self.model.transcribe(
                video_path,
                language="en",
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500
                ),
                word_timestamps=True,
                condition_on_previous_text=True
            )

            segments = list(segments)

            print(f"Detected Language : {info.language}")
            print(f"Confidence        : {info.language_probability:.2f}")
            print()

            # --------------------------------------------------
            # TXT
            # --------------------------------------------------

            txt_path = os.path.join(
                self.txt_folder,
                filename + ".txt"
            )

            with open(txt_path, "w", encoding="utf-8") as f:

                for segment in segments:
                    f.write(segment.text.strip() + "\n")

            # --------------------------------------------------
            # JSON
            # --------------------------------------------------

            transcript_json = {
                "video_name": filename,
                "language": info.language,
                "segments": []
            }

            for idx, segment in enumerate(segments, start=1):

                transcript_json["segments"].append({

                    "id": idx,

                    "start": round(segment.start, 2),

                    "end": round(segment.end, 2),

                    "text": segment.text.strip(),

                    "speaker": "Unknown",

                    "module": "",

                    "topic": "",

                    "keywords": []

                })

            json_path = os.path.join(
                self.json_folder,
                filename + ".json"
            )

            with open(json_path, "w", encoding="utf-8") as f:

                json.dump(
                    transcript_json,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            # --------------------------------------------------
            # SRT
            # --------------------------------------------------

            srt_path = os.path.join(
                self.srt_folder,
                filename + ".srt"
            )

            with open(srt_path, "w", encoding="utf-8") as f:

                for i, segment in enumerate(segments, start=1):

                    f.write(f"{i}\n")

                    f.write(
                        f"{self.format_timestamp(segment.start)} --> "
                        f"{self.format_timestamp(segment.end)}\n"
                    )

                    f.write(segment.text.strip())
                    f.write("\n\n")

            # --------------------------------------------------
            # Metadata
            # --------------------------------------------------

            processing_time = round(
                time.time() - start_time,
                2
            )

            metadata = {

                "video_name": filename,

                "model": self.model_size,

                "language": info.language,

                "device": self.device,

                "compute_type": self.compute_type,

                "processing_time_seconds": processing_time,

                "created_at": datetime.now().isoformat()

            }

            metadata_path = os.path.join(
                self.metadata_folder,
                filename + ".metadata.json"
            )

            with open(metadata_path, "w", encoding="utf-8") as f:

                json.dump(
                    metadata,
                    f,
                    indent=4
                )

            print("=" * 60)
            print(" Transcript Generated Successfully!")
            print("=" * 60)

            print(f"Time Taken : {processing_time} sec")
            print()

            print("Generated Files")

            print(f"TXT      : {txt_path}")
            print(f"JSON     : {json_path}")
            print(f"SRT      : {srt_path}")
            print(f"Metadata : {metadata_path}")

            print("=" * 60)

        except Exception:
            print("=" * 60)
            print(" Error while generating transcript")
            print("=" * 60)
            traceback.print_exc()