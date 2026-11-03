# Photo Collage Kit 📷✨

A small, reusable **Pillow / Python** toolbox for scrapbook-style photo editing: real-photo cutouts, soft pencil outlines, colored halos, fogged-glass lettering, and transparent music-player cards.

Originally distilled from experiments with music-card, café sticker, and fog-glass collage layouts. The **code is reusable**, not a generative model or a background-removal service. No real personal photographs, credentials, or third-party screenshot assets are included in this public repository.

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m examples.demo --output-dir demo_outputs
python -m unittest discover -s tests -v
```

The demo creates three **synthetic** PNGs: `outlined_cutout_demo.png`, `fog_glass_demo.png`, and `music_card_demo.png`. No photo uploads or AI services required.

## Components

| Module | Reusable capabilities |
|---|---|
| `design_scripts.core.cutout` | Apply supplied alpha masks; feather, trim and composite transparent layers |
| `design_scripts.core.outline` | Sticker borders, cream/pencil contours around masked subjects |
| `design_scripts.core.glow` | Soft elliptical color backing / light halos |
| `design_scripts.core.fog` | Frosted copy, negative lettering reveal masks, deterministic droplets |
| `design_scripts.core.player` | Translucent music-player UI, square photo crop, icons and progress track |
| `design_scripts.core.doodles` | Stars, sparkles and earphone wires |

The `design_scripts.templates` package combines these into `outlined_cutout_template`, `fog_glass_template`, and `music_card_template`. Templates accept `PIL.Image` inputs and return `PIL.Image` outputs.

## One-minute example

```python
from PIL import Image
from design_scripts.templates.music_card_template import build_music_card

photo = Image.open("my_photo.jpg")
poster = build_music_card(photo, photo, title="Little Joys", subtitle="Our Café Date")
poster.save("music_card.png")
```

For sticker cutouts, supply one or more **RGBA images with transparent backgrounds**, positioned as `(image, (x, y))`:

```python
from PIL import Image
from design_scripts.templates.outlined_cutout_template import build_outlined_cutout

background = Image.open("my_photo.jpg")
subject = Image.open("my_cutout.png").convert("RGBA")  # externally segmented
result = build_outlined_cutout(background, [(subject, (350, 980))])
result.save("stickers.png")
```

For fog-glass handwriting:

```python
from PIL import Image
from design_scripts.templates.fog_glass_template import build_fog_glass

photo = Image.open("my_photo.jpg")
result = build_fog_glass(photo, ["Little", "Joys"])
result.save("fog_glass.png")
```

## Limits & design decisions

- **Cutout masks are inputs.** The kit does not pretend to run SAM/rembg or remove backgrounds automatically. Provide a transparent PNG or `PIL.Image` mask from your own segmentation method.
- Pencil outline is a dilation-based approximation, not genuine physical pencil media. Fine edges benefit from high-quality masks and slight hand cleanup.
- Glass player is a **decorative mockup**, not working audio playback. Example track names and timestamps are placeholders.
- `ImageOps.fit` applies aspect-fill cropping to photos and album art; original pixels are not generatively repainted. You can edit template crop/placement rules for your photo.
- Fonts are loaded from common system locations; missing CJK fonts may require passing or installing an appropriate font.
- This public repo is **scripts only**. The related design-method skills live separately in the private `Design-skill` library.

## Provenance

This is a new modular implementation informed by our own photo-compositing experiments and creator-described editing operations, not a copy of another author's source code or illustration stickers. License: MIT.
