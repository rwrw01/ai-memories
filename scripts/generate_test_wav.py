"""Generate sine wave WAV files for incremental STT testing.

Usage:
    python generate_test_wav.py                     # generates 1-5 min files
    python generate_test_wav.py --duration 60       # custom duration in seconds
    python generate_test_wav.py --output test.wav   # custom output path
"""

import struct
import math
import argparse
from pathlib import Path


def generate_sine_wav(
    path: str,
    duration: float = 5.0,
    sample_rate: int = 48000,
    freq: float = 440.0,
) -> int:
    """Generate a mono 16-bit PCM WAV with a sine wave. Returns file size in bytes."""
    num_samples = int(sample_rate * duration)
    data_bytes = num_samples * 2  # 16-bit = 2 bytes per sample

    with open(path, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_bytes))
        f.write(b"WAVE")
        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_bytes))
        for i in range(num_samples):
            sample = math.sin(2 * math.pi * freq * i / sample_rate)
            f.write(struct.pack("<h", int(sample * 32767)))

    return 44 + data_bytes


def main():
    parser = argparse.ArgumentParser(description="Generate test WAV files")
    parser.add_argument("--duration", type=int, help="Duration in seconds")
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args()

    out_dir = Path(__file__).parent / "test-audio"
    out_dir.mkdir(exist_ok=True)

    if args.duration:
        path = args.output or str(out_dir / f"test-{args.duration}s.wav")
        size = generate_sine_wav(path, duration=args.duration)
        print(f"  {path}: {size / 1024:.0f} KB ({args.duration}s)")
        return

    # Default: generate 1-5 minute files
    durations = [60, 120, 180, 240, 300]
    print("Generating test WAV files (48kHz mono 16-bit PCM):\n")
    for dur in durations:
        label = f"{dur // 60}min"
        path = str(out_dir / f"test-{label}.wav")
        size = generate_sine_wav(path, duration=dur)
        print(f"  {path}: {size / (1024 * 1024):.1f} MB ({dur}s)")

    print(f"\nFiles in: {out_dir}")


if __name__ == "__main__":
    main()
