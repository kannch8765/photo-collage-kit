"""Actual fog + negative lettering masking over a source photo."""
from __future__ import annotations
from PIL import Image, ImageFilter, ImageOps
from design_scripts.core.fog import make_frosted_background,handwriting_mask,reveal_through_fog,add_droplets
from design_scripts.core.doodles import draw_star_doodles


def build_fog_glass(scene:Image.Image,phrase_lines:list[str],start_xy=(120,180),
                    size=(1080,1920),font_size=135) -> Image.Image:
    clear=ImageOps.fit(scene.convert("RGB"),size,Image.Resampling.LANCZOS).convert("RGBA")
    fog=make_frosted_background(clear,blur_radius=max(10,round(size[0]*.036)))
    mask=handwriting_mask(size,phrase_lines,start_xy,font_size=font_size,
                         softness=max(1,round(size[0]*.004)))
    # Upper area: fog with a few erased letters. Lower area: blend back to original.
    out=reveal_through_fog(clear,fog,mask)
    ymin,ymax=round(size[1]*.39),round(size[1]*.52)
    grad=Image.new("L",size,0)
    pix=grad.load()
    for y in range(ymin,size[1]):
        value=round(255*min(1,max(0,(y-ymin)/max(1,ymax-ymin))))
        for x in range(size[0]):pix[x,y]=value
    out=Image.composite(clear,out,grad)
    out=add_droplets(out,seed=42,count=20,top_fraction=.39)
    out=draw_star_doodles(out,[(round(size[0]*.14),round(size[1]*.12)),(round(size[0]*.88),round(size[1]*.18))],size=max(8,size[0]//75))
    return out
