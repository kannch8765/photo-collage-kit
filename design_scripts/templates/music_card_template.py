"""One-call glass player collage; preserves source photo as the album-art raster."""
from __future__ import annotations
from PIL import Image, ImageFilter, ImageOps
from design_scripts.core.player import compose_small_player
from design_scripts.core.doodles import draw_earphone_wire,draw_star_doodles


def build_music_card(canvas:Image.Image,cover:Image.Image,
                     player_box=(190,285,890,1430),title="Little Joys",
                     subtitle="Cafe Vibes",size=(1080,1920)) -> Image.Image:
    out=ImageOps.fit(canvas.convert("RGB"),size,Image.Resampling.LANCZOS).convert("RGBA")
    out=out.filter(ImageFilter.GaussianBlur(max(10,round(size[0]*.034))))
    out=compose_small_player(out,player_box,cover,title=title,subtitle=subtitle)
    x1,y1,x2,y2=player_box
    out=draw_earphone_wire(out,[(x1+40,y2-30),(max(30,x1-65),round(y2*1.05)),(max(30,x1-100),round(y2*1.18))],width=max(2,size[0]//200))
    out=draw_star_doodles(out,[(round(size[0]*.10),round(size[1]*.1)),(round(size[0]*.89),round(size[1]*.12)),(round(size[0]*.87),round(size[1]*.88))],size=max(8,size[0]//75))
    return out
