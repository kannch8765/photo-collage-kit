"""Condensation effects and reproducible soft-erased handwriting masks."""
from __future__ import annotations

import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def make_frosted_background(image: Image.Image, blur_radius: float=18,
                            veil: tuple[int,int,int,int]=(242,244,236,72)) -> Image.Image:
    bg = image.convert("RGBA").filter(ImageFilter.GaussianBlur(blur_radius))
    bg.alpha_composite(Image.new("RGBA",bg.size,veil))
    return bg


def load_font(size: int, font_path: str | None=None):
    candidates = [font_path, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"]
    for f in candidates:
        if f:
            try:
                return ImageFont.truetype(f, size)
            except OSError:
                continue
    return ImageFont.load_default()


def handwriting_mask(size: tuple[int,int], lines: list[str], start_xy: tuple[int,int],
                     line_gap: int=12,font_size:int=140,font_path:str|None=None,
                     softness:float=5) -> Image.Image:
    mask=Image.new("L",size,0)
    d=ImageDraw.Draw(mask)
    font=load_font(font_size,font_path)
    x,y=start_xy
    for line in lines:
        d.text((x,y),line,fill=255,font=font,stroke_width=max(1,round(font_size/80)))
        box=d.textbbox((x,y),line,font=font)
        y=box[3]+line_gap
    return mask.filter(ImageFilter.GaussianBlur(softness)) if softness else mask


def reveal_through_fog(clear_scene:Image.Image,fog_scene:Image.Image,reveal_mask:Image.Image)->Image.Image:
    if clear_scene.size != fog_scene.size or clear_scene.size != reveal_mask.size:
        raise ValueError("All reveal layers must have matching dimensions")
    return Image.composite(clear_scene.convert("RGBA"), fog_scene.convert("RGBA"),reveal_mask.convert("L"))


def add_droplets(image:Image.Image,seed:int=42,count:int=22,
                top_fraction:float=0.48)->Image.Image:
    rng=random.Random(seed)
    out=image.convert("RGBA")
    d=ImageDraw.Draw(out,"RGBA")
    w,h=out.size
    margin=max(3,min(40,w//12))
    ymax=max(margin+1,round(h*top_fraction))
    for _ in range(count):
        x=rng.randint(margin,w-margin)
        y=rng.randint(margin,ymax)
        r=rng.randint(2,max(2,round(w/140)))
        d.ellipse((x-r,y-r,x+r,y+r),fill=(255,255,255,70))
        d.arc((x-r,y-r,x+r,y+r),200,315,fill=(255,255,255,150),width=1)
        if rng.random()<0.20:
            length=rng.randint(10,round(h*0.03)+10)
            d.line((x,y+r,x,y+r+length),fill=(245,245,240,65),width=max(1,w//450))
    return out
