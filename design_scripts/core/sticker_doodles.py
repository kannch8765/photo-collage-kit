"""Original, reusable pastel journal doodles on transparent RGBA layers.

All art is generated from geometric strokes: no external stickers or photos.
Use :func:`render_doodle` to export standalone PNGs, or
:func:`paste_doodle` to layer a doodle over an existing Pillow photo.
"""
from __future__ import annotations

import math
from typing import Mapping

from PIL import Image, ImageDraw, ImageFilter

DEFAULT_PALETTE = {
    "ink": "#B87488",
    "cream": "#FFF9EF",
    "pink": "#F5B8C8",
    "mint": "#9BCFC4",
    "blue": "#A7CBD9",
    "gold": "#EFCB79",
}
NAMES = ("heart", "sparkle", "bow", "sakura", "paw", "cat", "torii")


def _curve(controls: tuple[tuple[float, float], ...], steps: int = 22):
    """Cubic Bezier sample points for small hand-drawn curves."""
    a, b, c, d = controls
    return [
        (
            (1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*c[0]+t**3*d[0],
            (1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*c[1]+t**3*d[1],
        )
        for t in (i/steps for i in range(steps+1))
    ]


def _path(d: ImageDraw.ImageDraw, xy, fill, width: int):
    d.line(xy, fill=fill, width=width, joint="curve")
    radius = width // 2
    if radius:
        for x, y in (xy[0], xy[-1]):
            d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=fill)


def render_doodle(name: str, size: int = 128,
                  palette: Mapping[str, str] | None = None) -> Image.Image:
    """Render an original pencil/sticker motif as a transparent RGBA image.

    Sizes >= 32 are supported; 4x supersampling keeps lines soft when scaled.
    Names: heart, sparkle, bow, sakura, paw, cat, torii.
    """
    if name not in NAMES:
        raise ValueError(f"Unknown doodle {name!r}; choose from {', '.join(NAMES)}")
    if size < 32:
        raise ValueError("size must be at least 32 pixels")
    p = dict(DEFAULT_PALETTE)
    if palette:
        p.update(palette)
    scale = size * 4 / 100
    layer = Image.new("RGBA", (size*4, size*4), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    def xy(x, y): return (round(x*scale), round(y*scale))
    def box(x0,y0,x1,y1): return (*xy(x0,y0), *xy(x1,y1))
    def poly(points): return [xy(x,y) for x,y in points]
    def curve(points, col, sw=4): _path(d, poly(_curve(tuple(points))), col, round(sw*scale))
    def line(points, col, sw=4): _path(d, poly(points), col, round(sw*scale))

    if name == "heart":
        pts = (_curve(((50,79),(37,67),(15,54),(20,37))) +
               _curve(((20,37),(26,17),(46,28),(50,36))) +
               _curve(((50,36),(56,24),(78,17),(82,39))) +
               _curve(((82,39),(87,54),(65,72),(50,79))))
        d.polygon(poly(pts), fill=p["pink"])
        line(pts+[pts[0]],p["cream"],8)
        line(pts+[pts[0]],p["ink"],3)
        line([(29,42),(32,38),(37,37)],p["cream"],3)
    elif name == "sparkle":
        pts=[(50,12),(58,41),(87,50),(58,59),(50,88),(42,59),(13,50),(42,41)]
        d.polygon(poly(pts),fill=p["gold"])
        line(pts+[pts[0]],p["cream"],7)
        line(pts+[pts[0]],p["ink"],2)
        d.ellipse(box(77,16,83,22),fill=p["cream"])
        d.ellipse(box(15,74,20,79),fill=p["cream"])
    elif name == "bow":
        for pts in [[(48,50),(17,22),(12,38),(17,69),(48,55)],
                    [(52,50),(83,22),(88,38),(83,69),(52,55)]]:
            d.polygon(poly(pts),fill=p["pink"])
            line(pts+[pts[0]],p["cream"],7)
            line(pts+[pts[0]],p["ink"],3)
        line([(25,42),(45,51),(25,60)],p["cream"],3)
        line([(75,42),(55,51),(75,60)],p["cream"],3)
        d.rounded_rectangle(box(43,41,57,61),radius=round(6*scale),fill=p["cream"])
        d.rounded_rectangle(box(46,44,54,58),radius=round(3*scale),fill=p["pink"])
    elif name == "sakura":
        # Five overlapping circular petals: one gently scalloped silhouette.
        mask_small=Image.new("L",(100,100),0)
        md=ImageDraw.Draw(mask_small)
        for k in range(5):
            a=-math.pi/2+k*2*math.pi/5
            x,y=50+18*math.cos(a),50+18*math.sin(a)
            md.ellipse((x-20,y-20,x+20,y+20),fill=255)
        md.ellipse((33,33,67,67),fill=255)
        for radius, color in ((6,p["ink"]),(3,p["cream"]),(0,p["pink"])):
            layer_mask=(mask_small.filter(ImageFilter.MaxFilter(2*radius+1))
                        if radius else mask_small)
            layer.paste(color,(0,0),layer_mask.resize(layer.size,Image.Resampling.LANCZOS))
        d.ellipse(box(43,43,57,57),fill=p["gold"])
        for k in range(5):
            a=-math.pi/2+k*2*math.pi/5
            x,y=50+20*math.cos(a),50+20*math.sin(a)
            d.ellipse(box(x-2,y-2,x+2,y+2), fill=p["cream"])
    elif name == "paw":
        toes=[(21,38,32,53),(37,22,49,40),(56,22,68,40),(73,38,84,53)]
        for toe in toes:
            d.ellipse(box(*toe),fill=p["pink"],outline=p["cream"],width=round(4*scale))
        pts=_curve(((25,74),(25,60),(40,53),(47,55)))+_curve(((47,55),(54,49),(73,60),(76,73)))+_curve(((76,73),(74,91),(55,80),(50,78)))+_curve(((50,78),(44,82),(27,90),(25,74)))
        d.polygon(poly(pts),fill=p["pink"])
        line(pts+[pts[0]],p["cream"],6)
        line(pts+[pts[0]],p["ink"],2)
    elif name == "cat":
        pts=( [(23,51),(18,22),(38,34)] +
              _curve(((38,34),(45,32),(55,32),(63,34))) +
              [(82,22),(78,52)] +
              _curve(((78,52),(88,86),(12,87),(23,51))) )
        d.polygon(poly(pts),fill=p["cream"])
        line(pts+[pts[0]],p["ink"],4)
        d.polygon(poly([(22,34),(25,47),(36,37)]),fill=p["pink"])
        d.polygon(poly([(64,37),(77,34),(75,47)]),fill=p["pink"])
        for cx in (35,65):
            curve([(cx-5,62),(cx-2,57),(cx+2,57),(cx+5,62)],p["ink"],3)
            d.ellipse(box(cx-12,64,cx-3,70),fill=p["pink"])
        d.polygon(poly([(47,65),(53,65),(50,69)]),fill=p["ink"])
        curve([(42,72),(45,78),(49,73),(50,69)],p["ink"],2)
        curve([(50,69),(52,78),(56,76),(58,72)],p["ink"],2)
    elif name == "torii":
        line([(17,27),(83,27)],p["cream"],11)
        line([(17,27),(83,27)],p["pink"],7)
        line([(24,39),(76,39)],p["ink"],5)
        for xx in (34,66):
            line([(xx,40),(xx,83)],p["cream"],11)
            line([(xx,40),(xx,83)],p["pink"],7)
        line([(28,82),(40,82)],p["ink"],3)
        line([(60,82),(72,82)],p["ink"],3)
    return layer.resize((size,size),Image.Resampling.LANCZOS)


def paste_doodle(canvas: Image.Image, name: str, center: tuple[int,int],
                 size: int = 128, rotation: float = 0,
                 palette: Mapping[str,str] | None = None) -> Image.Image:
    """Paste a transparent doodle onto a copy of *canvas* without changing source pixels elsewhere."""
    out=canvas.convert("RGBA")
    icon=render_doodle(name,size,palette)
    if rotation:
        icon=icon.rotate(rotation, Image.Resampling.BICUBIC, expand=True)
    x=round(center[0]-icon.width/2)
    y=round(center[1]-icon.height/2)
    overlay=Image.new("RGBA",out.size,(0,0,0,0))
    overlay.paste(icon,(x,y))
    return Image.alpha_composite(out,overlay)
