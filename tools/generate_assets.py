"""Generate UI images and the countdown beep without external dependencies."""

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


def read_rgba_png(path: Path) -> tuple[int, int, list[bytes]]:
    """Read the bundled, non-interlaced RGBA logo without image dependencies."""
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"Not a PNG: {path}")
    offset = 8
    compressed = bytearray()
    while offset < len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        offset += length + 12
        if kind == b"IHDR":
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if (depth, color, compression, filtering, interlace) != (8, 6, 0, 0, 0):
                raise ValueError("Logo must be a non-interlaced 8-bit RGBA PNG")
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
    raw = zlib.decompress(compressed)
    stride = width * 4
    rows = []
    previous = bytearray(stride)
    position = 0
    for _ in range(height):
        filter_type = raw[position]
        position += 1
        row = bytearray(raw[position:position + stride])
        position += stride
        for index in range(stride):
            left = row[index - 4] if index >= 4 else 0
            above = previous[index]
            upper_left = previous[index - 4] if index >= 4 else 0
            if filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = above
            elif filter_type == 3:
                predictor = (left + above) // 2
            elif filter_type == 4:
                estimate = left + above - upper_left
                distances = (abs(estimate - left), abs(estimate - above), abs(estimate - upper_left))
                predictor = (left, above, upper_left)[distances.index(min(distances))]
            elif filter_type == 0:
                predictor = 0
            else:
                raise ValueError(f"Unsupported PNG filter: {filter_type}")
            row[index] = (row[index] + predictor) & 255
        rows.append(bytes(row))
        previous = row
    return width, height, rows


def write_branded_png(path: Path, width: int, height: int, logo: tuple[int, int, list[bytes]], splash: bool = False) -> None:
    source_width, source_height, source_rows = logo
    width_limit = width * (0.38 if splash else 0.88)
    height_limit = height * (0.42 if splash else 0.80)
    scale = min(width_limit / source_width, height_limit / source_height)
    logo_width = round(source_width * scale)
    logo_height = round(source_height * scale)
    left = (width - logo_width) // 2
    top = (height - logo_height) // 2
    background = bytes((24, 24, 24, 255)) * width
    rows = []
    for y in range(height):
        row = bytearray(background)
        if top <= y < top + logo_height:
            source_y = min(source_height - 1, int((y - top + 0.5) / scale))
            source_row = source_rows[source_y]
            for x in range(logo_width):
                source_x = min(source_width - 1, int((x + 0.5) / scale))
                source_index = source_x * 4
                alpha = source_row[source_index + 3]
                if alpha:
                    target_index = (left + x) * 4
                    for channel in range(3):
                        row[target_index + channel] = (source_row[source_index + channel] * alpha + 24 * (255 - alpha)) // 255
        rows.append(b"\x00" + row)
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += png_chunk(b"IHDR", header)
    data += png_chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
    data += png_chunk(b"IEND", b"")
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
    # start.wav and complete.wav are supplied recordings, not generated tones.
    logo = read_rgba_png(ROOT / "images/logo-xteam.png")
    write_branded_png(ROOT / "images/icon-focus-hd.png", 290, 218, logo)
    write_branded_png(ROOT / "images/icon-side-hd.png", 108, 81, logo)
    write_branded_png(ROOT / "images/icon-focus-sd.png", 214, 144, logo)
    write_branded_png(ROOT / "images/icon-side-sd.png", 80, 60, logo)
    write_branded_png(ROOT / "images/splash-hd.png", 1280, 720, logo, splash=True)
    write_branded_png(ROOT / "images/splash-fhd.png", 1920, 1080, logo, splash=True)
    write_rounded_png(ROOT / "images/rounded-wide.png", 1146, 77, 10)
    write_rounded_png(ROOT / "images/rounded-small.png", 534, 75, 10)


if __name__ == "__main__":
    main()
