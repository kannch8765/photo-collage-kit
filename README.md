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
| `design_scripts.core.speckle` | Standalone full-frame furry glass (`full_frame_spray_frost`); optional, separate stippled reveal masks |
| `design_scripts.core.player` | Translucent music-player UI, square photo crop, icons and progress track |
| `design_scripts.core.doodles` | Stars, sparkles and earphone wires |
| `design_scripts.core.sticker_doodles` | Transparent pastel journal stickers: heart, sparkle, bow, sakura, paw, cat, torii |

The `design_scripts.templates` package combines these into `outlined_cutout_template`, `fog_glass_template`, and `music_card_template`. Templates accept `PIL.Image` inputs and return `PIL.Image` outputs.

[Journal sticker pack and demo](JOURNAL_STICKERS.md) — seven original, photo-free motifs; export transparent PNGs with `python -m examples.sticker_sheet`.

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

## Speckled / spray-frosted glass

The sprayed, “hairy” frost variant adds fine condensation grain and a stochastic soft edge around a clear photograph. Unlike plain Gaussian blur, the edge has tiny particles instead of a perfectly smooth gradient. Use a focal ellipse over the food or subject; adjust `edge_width` and `grain_strength` to tune the amount of frosting.

```python
from PIL import Image
from design_scripts.core.speckle import reveal_photo_in_spray_frost

photo = Image.open("my_photo.jpg")
w, h = photo.size
result = reveal_photo_in_spray_frost(
    photo, (round(w * .05), round(h * .1), round(w * .95), round(h * .95)),
    edge_width=45, grain_strength=.6, seed=42,
)
result.save("spray_frost.png")
```

The foreground remains the original photo, not an AI redraw. For object-specific cutout boundaries, supply a separately segmented alpha mask.

## Full-frame furry / speckled glass filter

The **glass itself is a standalone effect**, without cutting out a subject, applying an outline, or placing any stickers. This reproduces the tutorial’s first step (the entire photo is covered in textured frost). Use another module **later** to layer a sharp subject on top if desired.

```bash
python -m examples.fullframe_frost --input my_photo.jpg --output frosted.png \
  --blur 24 --mist .23 --grain .67 --seed 42
```

Or in Python:

```python
from PIL import Image
from design_scripts.core.speckle import full_frame_spray_frost

frosted = full_frame_spray_frost(Image.open("my_photo.jpg"), grain_strength=.67)
frosted.save("frosted.png")
```

Only three parameters are needed to explore the material: `blur_radius` controls defocus, `mist_strength` controls milky translucency, and `grain_strength` controls the fuzzy sprayed microtexture. The filter preserves the entire image dimensions, never crops or isolates a foreground object, and is deterministic with a `seed`. For comparison, use `grain_strength=0` for simple smooth frosting. The original app’s “size 0 / strength 100” slider values do not translate directly to Pillow.

## Limits & design decisions

- **Cutout masks are inputs.** The kit does not pretend to run SAM/rembg or remove backgrounds automatically. Provide a transparent PNG or `PIL.Image` mask from your own segmentation method.
- Pencil outline is a dilation-based approximation, not genuine physical pencil media. Fine edges benefit from high-quality masks and slight hand cleanup.
- Glass player is a **decorative mockup**, not working audio playback. Example track names and timestamps are placeholders.
- `ImageOps.fit` applies aspect-fill cropping to photos and album art; original pixels are not generatively repainted. You can edit template crop/placement rules for your photo.
- Fonts are loaded from common system locations; missing CJK fonts may require passing or installing an appropriate font.
- This public repo is **scripts only**. The related design-method skills live separately in the private `Design-skill` library.

## Provenance

This is a new modular implementation informed by our own photo-compositing experiments and creator-described editing operations, not a copy of another author's source code or illustration stickers. License: MIT.
