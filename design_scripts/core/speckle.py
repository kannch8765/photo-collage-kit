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


def full_frame_spray_frost(
    image: Image.Image,
    *,
    blur_radius: float = 24.0,
    mist_strength: float = 0.23,
    grain_strength: float = 0.53,
    mist_color: tuple[int, int, int] = (235, 228, 219),
    seed: int = 42,
) -> Image.Image:
    """Apply only a full-canvas furry/speckled frosted-glass filter.

    No subjects are cut out, cleared, outlined, or rearranged. The input
    image is unchanged and output dimensions are the same.

    blur_radius controls soft defocus; mist_strength is milky haze opacity;
    grain_strength controls fine condensation granules (all independent).
    """
    if blur_radius < 0 or not (0 <= mist_strength <= 1) or not (0 <= grain_strength <= 1):
        raise ValueError("blur_radius must be nonnegative; strengths must be 0..1")
    if len(mist_color) != 3 or any(not (0 <= v <= 255) for v in mist_color):
        raise ValueError("mist_color must be an RGB color")

    src = image.convert("RGB")
    width, height = src.size
    if width < 1 or height < 1:
        raise ValueError("image must have positive dimensions")
    rng = random.Random(seed)
    blurred = src.filter(ImageFilter.GaussianBlur(blur_radius))

    # Large translucent clouds make the frosted layer less flat.
    cw, ch = max(2, width // 45), max(2, height // 45)
    clouds = Image.frombytes("L", (cw, ch), rng.randbytes(cw * ch))
    clouds = clouds.resize(src.size, Image.Resampling.BICUBIC)
    clouds = clouds.filter(ImageFilter.GaussianBlur(1.7))
    opacity = clouds.point(lambda v: max(0, min(255, round(
        255 * mist_strength + (v - 128) * 0.45 * mist_strength
    ))))
    out = Image.composite(Image.new("RGB", src.size, mist_color), blurred, opacity)

    if grain_strength > 0:
        # Fine stipples and slightly larger grains with a deterministic seed.
        dust = Image.frombytes("L", src.size, rng.randbytes(width * height))
        dust = dust.filter(ImageFilter.GaussianBlur(0.28))
        dust = dust.point(lambda v: max(0, min(255, round(
            128 + (v - 128) * grain_strength * 0.28
        ))))
        mw, mh = max(2, width // 5), max(2, height // 5)
        mid = Image.frombytes("L", (mw, mh), rng.randbytes(mw * mh))
        mid = mid.resize(src.size, Image.Resampling.BILINEAR)
        mid = mid.point(lambda v: max(0, min(255, round(
            128 + (v - 128) * grain_strength * 0.12
        ))))
        channels = []
        for channel in out.split():
            channel = ImageChops.add(channel, dust, offset=-128)
            channel = ImageChops.add(channel, mid, offset=-128)
            channels.append(channel)
        out = Image.merge("RGB", channels)

    return out.convert("RGBA")
