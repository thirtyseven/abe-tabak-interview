"""Compatibility entry point for the recording-driven reader build."""

from pathlib import Path

from build_reader import build


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1] / "recordings" / "tape-1.json")
