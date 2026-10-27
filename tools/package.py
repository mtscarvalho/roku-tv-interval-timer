"""Build a deterministic sideloadable Roku ZIP using only Python's standard library."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from generate_assets import main as generate_assets


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "dist/intervalo-tv.zip"
INCLUDED = ("manifest", "source", "components", "images", "audio")


def main() -> None:
    generate_assets()
    PACKAGE.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(PACKAGE, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in INCLUDED:
            path = ROOT / name
            if path.is_file():
                archive.write(path, path.relative_to(ROOT).as_posix())
            else:
                for child in sorted(path.rglob("*")):
                    if child.is_file():
                        archive.write(child, child.relative_to(ROOT).as_posix())
    print(f"Pacote criado: {PACKAGE}")


if __name__ == "__main__":
    main()

