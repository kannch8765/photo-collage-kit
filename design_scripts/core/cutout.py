"""Photo-preserving cutout helpers. Segmentation masks are supplied by the caller."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PIL import Image, ImageChops, ImageFilter

BBox = tuple[int, int, int, int]


@dataclass(frozen=True)
class CutoutResult:
    image: Image.Image
    bbox: BBox


def ensure_rgba(image: Image.Image) -> Image.Image:
    return image.convert("RGBA")


def ensure_l(mask: Image.Image) -> Image.Image:
    return mask.convert("L")


def apply_alpha_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    """Multiply source alpha by mask instead of accidentally restoring transparent pixels."""
    source = ensure_rgba(image)
    matte = ensure_l(mask).resize(source.size, Image.Resampling.BILINEAR)
    result = source.copy()
    result.putalpha(ImageChops.multiply(source.getchannel("A"), matte))
    return result


def feather_mask(mask: Image.Image, radius: float = 2.0) -> Image.Image:
    matte = ensure_l(mask)
    return matte.filter(ImageFilter.GaussianBlur(radius)) if radius > 0 else matte.copy()


def trim_to_alpha(image: Image.Image, padding: int = 0) -> CutoutResult:
    image = ensure_rgba(image)
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("Cannot trim a fully transparent image")
    l, t, r, b = bounds
    rect = (max(0, l-padding), max(0, t-padding), min(image.width, r+padding), min(image.height, b+padding))
    return CutoutResult(image.crop(rect), rect)


def paste_rgba(base: Image.Image, overlay: Image.Image, xy: tuple[int, int]) -> Image.Image:
    """Alpha composite, including partly off-canvas overlays."""
    out = ensure_rgba(base)
    layer = ensure_rgba(overlay)
    x, y = xy
    left, top = max(0, x), max(0, y)
    right, bottom = min(out.width, x+layer.width), min(out.height, y+layer.height)
    if right <= left or bottom <= top:
        return out
    cropped = layer.crop((left-x, top-y, right-x, bottom-y))
    out.alpha_composite(cropped, (left, top))
    return out


def union_bbox(bboxes: Iterable[BBox]) -> BBox:
    b = list(bboxes)
    return (min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b)) if b else (0,0,0,0)


def dilate_mask(mask: Image.Image, pixels: int = 8) -> Image.Image:
    layer = ensure_l(mask)
    for _ in range(max(0, pixels)):
        layer = layer.filter(ImageFilter.MaxFilter(3))
    return layer


def erode_mask(mask: Image.Image, pixels: int = 8) -> Image.Image:
    layer = ensure_l(mask)
    for _ in range(max(0, pixels)):
        layer = layer.filter(ImageFilter.MinFilter(3))
    return layer


def alpha_bbox(image: Image.Image) -> BBox:
    return ensure_rgba(image).getchannel("A").getbbox() or (0,0,0,0)
