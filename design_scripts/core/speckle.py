"""Speckled / spray-frosted glass, unlike smooth Gaussian blur.

Only real-photo Pillow compositing: no generative reconstruction.
"""
from __future__ import annotations

import random
from PIL import Image, ImageChops, ImageDraw, ImageFilter


def grain_frosted_background(
    image: Image.Image,
    blur_radius: float = 22,
    veil_color: tuple[int, int, int] = (225, 232, 220),
    veil_strength: float = 0.20,
    grain_strength: float = 0.13,
    seed: int = 42,
) -> Image.Image:
    """Blur and tint a photo, adding seeded micro-condensation grain.

    Grain is an RGB luminance perturbation, not lossy pixelation. The source
    photo is never modified in place.
    """
    if blur_radius < 0 or not 0 <= veil_strength <= 1 or not 0 <= grain_strength <= 1:
        raise ValueError("blur_radius must be nonnegative; strengths are 0..1")
    src = image.convert("RGB")
    fog = src.filter(ImageFilter.GaussianBlur(blur_radius))
    fog = Image.blend(fog, Image.new("RGB", src.size, veil_color), veil_strength)
    if grain_strength == 0:
        return fog.convert("RGBA")

    rng = random.Random(seed)
    noise = Image.frombytes("L", src.size, rng.randbytes(src.width * src.height))
    # 128 -> zero perturbation, preserving overall luminance.
    noise = noise.point(lambda v: round(128 + (v - 128) * grain_strength))
    channels = [ImageChops.add(ch, noise, offset=-128) for ch in fog.split()]
    return Image.merge("RGB", channels).convert("RGBA")


def spray_reveal_mask(
    size: tuple[int, int],
    focus_box: tuple[int, int, int, int],
    edge_width: int = 45,
    grain_strength: float = 0.60,
    seed: int = 42,
) -> Image.Image:
    """Build a soft but irregular speckled alpha mask (L mode).

    White reveals the original crisp image, black exposes the fuzzy frosting.
    The ellipse's inside remains opaque; only the border gets sprinkled.
    """
    if edge_width < 1 or not 0 <= grain_strength <= 1:
        raise ValueError("edge_width >= 1 and 0 <= grain_strength <= 1 required")
    w, h = size
    if w < 1 or h < 1:
        raise ValueError("size must be positive")
    x1, y1, x2, y2 = focus_box
    if x2 <= x1 or y2 <= y1:
        raise ValueError("focus_box must have positive width and height")

    shape = Image.new("L", size, 0)
    ImageDraw.Draw(shape).ellipse(focus_box, fill=255)
    soft = shape.filter(ImageFilter.GaussianBlur(edge_width))

    # Preserve the central subject perfectly crisp.
    inner = Image.new("L", size, 0)
    inset = max(2, round(edge_width * 1.5))
    if (x2 - x1) > 2 * inset and (y2 - y1) > 2 * inset:
        ImageDraw.Draw(inner).ellipse(
            (x1 + inset, y1 + inset, x2 - inset, y2 - inset), fill=255
        )

    if grain_strength == 0:
        return ImageChops.lighter(soft, inner)

    rng = random.Random(seed)
    noise = Image.frombytes("L", size, rng.randbytes(w * h))
    # Bounded perturbation of the smooth alpha creates spray-paint edge dots.
    perturb = noise.point(lambda v: round(128 + (v - 128) * grain_strength))
    irregular = ImageChops.add(soft, perturb, offset=-128)

    # Do not sprinkle random clear dots over the entire canvas: limit to the
    # area around the original focus window.
    outer = Image.new("L", size, 0)
    ImageDraw.Draw(outer).ellipse(
        (x1 - 2 * edge_width, y1 - 2 * edge_width,
         x2 + 2 * edge_width, y2 + 2 * edge_width), fill=255
    )
    irregular = ImageChops.multiply(irregular, outer)
    irregular = irregular.filter(ImageFilter.GaussianBlur(0.55))
    return ImageChops.lighter(irregular, inner)


def reveal_photo_in_spray_frost(
    photo: Image.Image,
    focus_box: tuple[int, int, int, int],
    *,
    blur_radius: float = 22,
    edge_width: int = 45,
    grain_strength: float = 0.60,
    seed: int = 42,
) -> Image.Image:
    """Convenience composition for a crisp photo emerging from frosted grain."""
    clear = photo.convert("RGBA")
    fog = grain_frosted_background(photo, blur_radius=blur_radius, seed=seed)
    mask = spray_reveal_mask(
        photo.size, focus_box, edge_width=edge_width,
        grain_strength=grain_strength, seed=seed
    )
    return Image.composite(clear, fog, mask)
