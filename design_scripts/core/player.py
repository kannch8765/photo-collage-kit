"""A visually decorative glass music card. Not an audio player."""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter, ImageOps
from .fog import load_font


def draw_glass_panel(canvas:Image.Image,box:tuple[int,int,int,int],
                     fill=(44,58,50,143),outline=(250,248,240,130),radius:int=28)->Image.Image:
    out=canvas.convert("RGBA")
    panel=Image.new("RGBA",out.size)
    d=ImageDraw.Draw(panel)
    d.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=2)
    out.alpha_composite(panel)
    return out


def draw_progress_bar(d: ImageDraw.ImageDraw,x1:int,y:int,x2:int,value:float):
    d.line((x1,y,x2,y),fill=(236,234,228,120),width=3)
    cx=round(x1+(x2-x1)*max(0,min(1,value)))
    d.line((x1,y,cx,y),fill=(252,249,242,240),width=3)
    d.ellipse((cx-5,y-5,cx+5,y+5),fill=(252,250,244,245))


def draw_music_controls(d:ImageDraw.ImageDraw,center:tuple[int,int],scale:float=1):
    cx,cy=center; s=scale
    # Previous, pause, next. Intentionally consistent geometry.
    white=(250,249,243,235)
    d.polygon([(cx-42*s,cy),(cx-24*s,cy-10*s),(cx-24*s,cy+10*s)],fill=white)
    d.line((cx-45*s,cy-10*s,cx-45*s,cy+10*s),fill=white,width=max(1,round(3*s)))
    for shift in (-6,6):
        d.rounded_rectangle((cx+(shift-3)*s,cy-11*s,cx+(shift+3)*s,cy+11*s),radius=2,fill=white)
    d.polygon([(cx+24*s,cy-10*s),(cx+24*s,cy+10*s),(cx+42*s,cy)],fill=white)
    d.line((cx+45*s,cy-10*s,cx+45*s,cy+10*s),fill=white,width=max(1,round(3*s)))


def compose_small_player(canvas:Image.Image,box:tuple[int,int,int,int],cover:Image.Image,
                         title:str="Little Joys",subtitle:str="Cafe Vibes",
                         progress:float=0.36)->Image.Image:
    x1,y1,x2,y2=box
    panel_width=x2-x1
    pad=max(12,round(panel_width*0.07))
    cw=panel_width-2*pad
    title_size=max(12,round(panel_width*0.082))
    sub_size=max(10,round(panel_width*0.06))
    required_height=pad+cw+round(panel_width*0.45)
    if y2-y1<required_height:
        raise ValueError(f"Player box too short: need at least {required_height}px high")
    out=draw_glass_panel(canvas,box)
    cover=ImageOps.fit(cover.convert("RGB"),(cw,cw),Image.Resampling.LANCZOS,centering=(0.5,0.5)).convert("RGBA")
    alpha=Image.new("L",(cw,cw),0)
    ImageDraw.Draw(alpha).rounded_rectangle((0,0,cw-1,cw-1),radius=round(cw*0.05),fill=255)
    cover.putalpha(alpha)
    out.alpha_composite(cover,(x1+pad,y1+pad))
    d=ImageDraw.Draw(out)
    ty=y1+pad+cw+round(panel_width*0.05)
    d.text((x1+pad,ty),title,font=load_font(title_size),fill=(253,251,243,245))
    d.text((x1+pad,ty+title_size+4),subtitle,font=load_font(sub_size),fill=(246,242,234,185))
    py=ty+title_size+sub_size+round(panel_width*0.075)
    draw_progress_bar(d,x1+pad,py,x2-pad,progress)
    d.text((x1+pad,py+8),"0:54",font=load_font(max(8,round(sub_size*0.75))),fill=(246,242,234,190))
    right_label="-3:32"
    rb=d.textbbox((0,0),right_label,font=load_font(max(8,round(sub_size*0.75))))
    d.text((x2-pad-(rb[2]-rb[0]),py+8),right_label,font=load_font(max(8,round(sub_size*0.75))),fill=(246,242,234,190))
    draw_music_controls(d,((x1+x2)//2,py+round(panel_width*0.12)),scale=max(0.6,panel_width/330))
    return out
