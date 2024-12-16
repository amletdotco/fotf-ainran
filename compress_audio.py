import os
from pydub import AudioSegment

# Directory containing audio files
input_dir = "audio-raw"
output_dir = "audio"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Target bitrate for compression (adjust for quality vs. size)
TARGET_BITRATE = "128k"


def compress_audio(file_path, output_path):
    # Determine file format based on extension
    file_ext = file_path.split(".")[-1].lower()
    if file_ext not in ["wav", "mp3"]:
        print(f"Skipping unsupported file format: {file_path}")
        return

    try:
        # Load audio
        audio = AudioSegment.from_file(file_path)
        # Export with target bitrate
        audio.export(output_path, format="mp3", bitrate=TARGET_BITRATE)
        print(f"Compressed {file_path} -> {output_path}")
    except Exception as e:
        print(f"Failed to compress {file_path}: {e}")


def main():
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        if os.path.isfile(file_path):
            output_path = os.path.join(
                output_dir, os.path.splitext(file_name)[0] + ".mp3"
            )
            compress_audio(file_path, output_path)


if __name__ == "__main__":
    main()
