"""Photo-fidelity-first sticker collage. Each subject must already have alpha."""
from __future__ import annotations
from PIL import Image, ImageFilter, ImageOps
from design_scripts.core.glow import add_soft_halo
from design_scripts.core.outline import add_pencil_outline
from design_scripts.core.cutout import alpha_bbox, paste_rgba, union_bbox
from design_scripts.core.doodles import draw_star_doodles, draw_sparkles


def build_outlined_cutout(background:Image.Image,
                          subject_layers:list[tuple[Image.Image,tuple[int,int]]],
                          halo_color=(188,190,110,95),
                          size=(1080,1920)) -> Image.Image:
    """Place subject layers at the original-layer top-left, then outline with padding."""
    bg=ImageOps.fit(background.convert("RGB"),size,Image.Resampling.LANCZOS).convert("RGBA")
    bg=bg.filter(ImageFilter.GaussianBlur(max(2,round(size[0]*.04))))
    positions=[]
    for layer,(x,y) in subject_layers:
        box=alpha_bbox(layer)
        if box!=(0,0,0,0):
            positions.append((x+box[0],y+box[1],x+box[2],y+box[3]))
    if positions:
        bg=add_soft_halo(bg,union_bbox(positions),color=halo_color,
                        blur=max(10,round(size[0]*.075)),expand=.25)
    for layer,(x,y) in subject_layers:
        border_width=max(3,round(size[0]*.007))
        under=border_width+4
        pad=max(under+8,16)
        outlined=add_pencil_outline(layer,top_width=border_width,under_width=under,padding=pad)
        bg=paste_rgba(bg,outlined,(x-pad,y-pad))
    w,h=size
    bg=draw_star_doodles(bg,[(int(w*.14),int(h*.12)),(int(w*.89),int(h*.18)),(int(w*.82),int(h*.86))],size=max(7,w//80))
    bg=draw_sparkles(bg,[(int(w*.12),int(h*.21)),(int(w*.91),int(h*.71))],size=max(7,w//90))
    return bg
