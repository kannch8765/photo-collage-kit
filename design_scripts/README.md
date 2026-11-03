# design_scripts

Reusable visual building blocks extracted from the recent collage experiments.

## Core modules
- `core/cutout.py` — alpha-mask cleanup, trimming, feathering, and compositing helpers.
- `core/outline.py` — sticker / pencil outlines derived from alpha masks.
- `core/glow.py` — soft color halos, blobs, and spotlight shapes.
- `core/fog.py` — frosted backgrounds, handwriting reveal masks, and droplets.
- `core/player.py` — glass music-player panel primitives.
- `core/doodles.py` — stars, sparkles, circles, earphone wires.

## Templates
- `templates/outlined_cutout_template.py`
- `templates/fog_glass_template.py`
- `templates/music_card_template.py`

Each template is intentionally lightweight: it wires together the shared modules and is meant to be copied or adapted per project.
