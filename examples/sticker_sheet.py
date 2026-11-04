"""Make a public-safe demo: seven original transparent journal stickers (no photos)."""
from pathlib import Path
from PIL import Image, ImageDraw
from design_scripts.core.sticker_doodles import NAMES, render_doodle


def create_sheet(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    sheet=Image.new("RGB",(1050,520),(255,249,243))
    draw=ImageDraw.Draw(sheet)
    for i, name in enumerate(NAMES):
        icon=render_doodle(name,210)
        icon.save(output_dir/f"{name}.png")
        x=30+(i%4)*255
        y=22+(i//4)*250
        sheet.paste(icon,(x,y),icon)
        draw.text((x+58,y+212),name,fill=(128,91,101))
    path=output_dir/"sticker_sheet.png"
    sheet.save(path)
    return path

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,default=Path("demo_outputs/stickers"))
    args=p.parse_args()
    print(create_sheet(args.output_dir))
