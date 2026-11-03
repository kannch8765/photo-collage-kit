"""Apply only full-frame spray-frost to a photo (no cutouts, no stickers)."""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image
from design_scripts.core.speckle import full_frame_spray_frost


def main() -> None:
    p = argparse.ArgumentParser(description="Full-frame fuzzy/speckled glass photo filter")
    p.add_argument("--input", required=True, type=Path, help="Local input image")
    p.add_argument("--output", required=True, type=Path, help="Output PNG path")
    p.add_argument("--blur", type=float, default=24)
    p.add_argument("--mist", type=float, default=.23)
    p.add_argument("--grain", type=float, default=.53)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    with Image.open(args.input) as source:
        image = full_frame_spray_frost(
            source, blur_radius=args.blur,
            mist_strength=args.mist,
            grain_strength=args.grain, seed=args.seed
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
