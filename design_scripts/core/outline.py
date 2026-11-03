"""Mask-derived sticker/pencil contour strokes, with padding to avoid edge clipping."""
from __future__ import annotations

from PIL import Image, ImageChops, ImageFilter
from .cutout import dilate_mask, ensure_rgba, ensure_l

RGBA = tuple[int, int, int, int]


def alpha_outline_mask(alpha: Image.Image, width: int = 10, blur: float = 1.0) -> Image.Image:
    alpha = ensure_l(alpha)
    border = ImageChops.subtract(dilate_mask(alpha, width), alpha)
    return border.filter(ImageFilter.GaussianBlur(blur)) if blur else border


def _paint(mask: Image.Image, color: RGBA) -> Image.Image:
    layer = Image.new("RGBA", mask.size, color)
    # Respect both the paint opacity and the mask opacity.
    layer.putalpha(mask.point(lambda p: (p * color[3]) // 255))
    return layer


def _pad(image: Image.Image, padding: int) -> Image.Image:
    image = ensure_rgba(image)
    canvas = Image.new("RGBA", (image.width + padding*2, image.height + padding*2))
    canvas.alpha_composite(image, (padding, padding))
    return canvas


def add_sticker_outline(image: Image.Image, color: RGBA = (250,248,240,255),
                        width: int = 10, blur: float = 1.0,
                        outer_shadow: bool = False, padding: int | None = None) -> Image.Image:
    padding = max(width + 8, 12) if padding is None else padding
    source = _pad(image, padding)
    alpha = source.getchannel("A")
    out = Image.new("RGBA", source.size)
    if outer_shadow:
        out.alpha_composite(_paint(alpha_outline_mask(alpha, width + 5, 3), (30,20,12,45)))
    out.alpha_composite(_paint(alpha_outline_mask(alpha, width, blur), color))
    out.alpha_composite(source)
    return out


def add_pencil_outline(image: Image.Image,
                       top_color: RGBA = (247,244,235,255),
                       under_color: RGBA = (90,80,70,70),
                       top_width: int = 8, under_width: int = 12,
                       padding: int | None = None) -> Image.Image:
    padding = max(under_width + 8, 16) if padding is None else padding
    source = _pad(image, padding)
    alpha = source.getchannel("A")
    out = Image.new("RGBA", source.size)
    out.alpha_composite(_paint(alpha_outline_mask(alpha, under_width, 2), under_color))
    out.alpha_composite(_paint(alpha_outline_mask(alpha, top_width, 0.8), top_color))
    out.alpha_composite(source)
    return out
