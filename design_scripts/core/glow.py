"""Translucent, photo-color sampled blob and ellipse spotlight layers."""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

RGBA = tuple[int,int,int,int]


def add_soft_halo(canvas: Image.Image, bbox: tuple[int,int,int,int], color: RGBA=(190,200,120,90),
                  blur: float=40, expand: float=0.18, opacity_scale: float=1.0) -> Image.Image:
    out = canvas.convert("RGBA")
    x1,y1,x2,y2 = bbox
    px,py = int((x2-x1)*expand),int((y2-y1)*expand)
    layer = Image.new("RGBA", out.size)
    ImageDraw.Draw(layer).ellipse((x1-px,y1-py,x2+px,y2+py), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    if opacity_scale != 1:
        alpha = layer.getchannel("A").point(lambda p: min(255, max(0,int(p*opacity_scale))))
        layer.putalpha(alpha)
    out.alpha_composite(layer)
    return out


def add_blob_shape(canvas: Image.Image, center: tuple[int,int], radii: tuple[int,int],
                  color: RGBA, blur: float=30) -> Image.Image:
    cx,cy=center; rx,ry=radii
    return add_soft_halo(canvas,(cx-rx,cy-ry,cx+rx,cy+ry),color=color,blur=blur,expand=0)
