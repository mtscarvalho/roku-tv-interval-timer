"""Generate the small, dependency-free PNG and WAV assets used by the channel."""

from __future__ import annotations

import math
import struct
import wave
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def write_wav(path: Path, notes: list[tuple[float, float]], volume: float = 0.38) -> None:
    rate = 44_100
    frames: list[bytes] = []
    for frequency, duration in notes:
        sample_count = int(rate * duration)
        for index in range(sample_count):
            envelope = min(1.0, index / (rate * 0.01))
            envelope *= min(1.0, (sample_count - index) / (rate * 0.025))
            signal = 0.0 if frequency == 0 else math.sin(2 * math.pi * frequency * index / rate)
            frames.append(struct.pack("<h", int(32767 * volume * envelope * signal)))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(b"".join(frames))


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)


def write_png(path: Path, width: int, height: int, splash: bool = False) -> None:
    dark = (24, 24, 24, 255)
    accent = (222, 11, 55, 255)
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) * (0.18 if splash else 0.28)
    ring = max(4, int(radius * 0.16))
    rows: list[bytes] = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            distance = math.hypot(x - center_x, y - center_y)
            row.extend(accent if radius - ring <= distance <= radius else dark)
        rows.append(bytes(row))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += png_chunk(b"IHDR", header)
    data += png_chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
    data += png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_rounded_png(path: Path, width: int, height: int, radius: int) -> None:
    samples = (0.125, 0.375, 0.625, 0.875)
    rows: list[bytes] = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            covered = 0
            for offset_y in samples:
                for offset_x in samples:
                    sample_x = x + offset_x
                    sample_y = y + offset_y
                    nearest_x = min(max(sample_x, radius), width - radius)
                    nearest_y = min(max(sample_y, radius), height - radius)
                    distance = math.hypot(sample_x - nearest_x, sample_y - nearest_y)
                    if distance <= radius:
                        covered += 1
            alpha = int(255 * covered / 16)
            row.extend((255, 255, 255, alpha))
        rows.append(bytes(row))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += png_chunk(b"IHDR", header)
    data += png_chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
    data += png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main() -> None:
    write_wav(ROOT / "audio/countdown.wav", [(880, 0.11), (0, 0.04)])
    write_wav(ROOT / "audio/complete.wav", [(660, 0.14), (0, 0.05), (880, 0.2)])
    write_png(ROOT / "images/icon-focus-hd.png", 290, 218)
    write_png(ROOT / "images/icon-side-hd.png", 108, 81)
    write_png(ROOT / "images/icon-focus-sd.png", 214, 144)
    write_png(ROOT / "images/icon-side-sd.png", 80, 60)
    write_png(ROOT / "images/splash-hd.png", 1280, 720, splash=True)
    write_png(ROOT / "images/splash-fhd.png", 1920, 1080, splash=True)
    write_rounded_png(ROOT / "images/rounded-wide.png", 1146, 77, 10)
    write_rounded_png(ROOT / "images/rounded-small.png", 534, 75, 10)


if __name__ == "__main__":
    main()

