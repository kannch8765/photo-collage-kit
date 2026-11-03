"""Generate three synthetic demo cards; no private photos and no cutout AI needed."""
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

from design_scripts.templates.outlined_cutout_template import build_outlined_cutout
from design_scripts.templates.fog_glass_template import build_fog_glass
from design_scripts.templates.music_card_template import build_music_card


def create_demo(outdir:Path,size=(540,960)) -> list[Path]:
    outdir.mkdir(parents=True,exist_ok=True)
    w,h=size
    scene=Image.new("RGB",size,(145,127,107))
    d=ImageDraw.Draw(scene)
    for i in range(8):
        y=round(h*(i+1)/9)
        d.line((0,y,w,y),fill=(174,155,126),width=6)
    d.ellipse((round(w*.25),round(h*.33),round(w*.85),round(h*.66)),fill=(233,219,186))
    d.ellipse((round(w*.34),round(h*.38),round(w*.76),round(h*.61)),fill=(188,133,72))
    d.ellipse((round(w*.40),round(h*.42),round(w*.70),round(h*.55)),fill=(224,184,88))
    d.ellipse((round(w*.07),round(h*.31),round(w*.26),round(h*.48)),fill=(205,186,154))
    d.rounded_rectangle((round(w*.08),round(h*.28),round(w*.25),round(h*.43)),radius=20,fill=(131,91,63))

    cut=Image.new("RGBA",(240,190),(0,0,0,0))
    dc=ImageDraw.Draw(cut)
    dc.ellipse((5,10,220,185),fill=(255,228,214,255))
    dc.ellipse((120,0,230,95),fill=(230,242,221,255))
    dc.arc((45,55,95,95),20,160,fill=(95,62,65,255),width=5)
    dc.arc((110,55,160,95),20,160,fill=(95,62,65,255),width=5)

    outfile=outdir/"outlined_cutout_demo.png"
    build_outlined_cutout(scene,[(cut,(160,540))],size=size).save(outfile)
    fog=outdir/"fog_glass_demo.png"
    build_fog_glass(scene,["Little", "Joys"],start_xy=(65,40),size=size,font_size=72).save(fog)
    music=outdir/"music_card_demo.png"
    build_music_card(scene,scene,player_box=(90,100,450,715),title="Little Joys",subtitle="Demo Mix",size=size).save(music)
    return [outfile,fog,music]


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",type=Path,default=Path("demo_outputs"))
    a=p.parse_args()
    for path in create_demo(a.output_dir):
        print(path)
