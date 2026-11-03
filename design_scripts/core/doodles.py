"""Reusable minimally decorative strokes: stars, sparkles and earbud wires."""
from __future__ import annotations
import math
from collections.abc import Iterable
from PIL import Image, ImageDraw


def _points(cx,cy,outer,inner):
    return [(cx+math.cos(math.pi*i/5-math.pi/2)*(outer if i%2==0 else inner),cy+math.sin(math.pi*i/5-math.pi/2)*(outer if i%2==0 else inner)) for i in range(10)]


def draw_star_doodles(canvas:Image.Image,positions:Iterable[tuple[int,int]],
                     color=(248,245,215,255),size:int=14)->Image.Image:
    out=canvas.convert("RGBA")
    d=ImageDraw.Draw(out)
    for x,y in positions:
        p=_points(x,y,size,size*.45)
        d.line(p+[p[0]],fill=color,width=max(1,size//7),joint="curve")
    return out


def draw_sparkles(canvas:Image.Image,positions:Iterable[tuple[int,int]],
                 color=(248,245,215,255),size:int=12)->Image.Image:
    out=canvas.convert("RGBA")
    d=ImageDraw.Draw(out)
    for x,y in positions:
        d.line((x-size,y,x+size,y),fill=color,width=2)
        d.line((x,y-size,x,y+size),fill=color,width=2)
    return out


def draw_earphone_wire(canvas:Image.Image,points:list[tuple[int,int]],
                      color=(250,250,244,230),width:int=6)->Image.Image:
    out=canvas.convert("RGBA")
    ImageDraw.Draw(out).line(points,fill=color,width=width,joint="curve")
    return out
