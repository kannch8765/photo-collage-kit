from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
from design_scripts.core.cutout import apply_alpha_mask, trim_to_alpha, paste_rgba
from design_scripts.core.outline import add_pencil_outline
from design_scripts.core.glow import add_soft_halo
from design_scripts.core.fog import handwriting_mask, reveal_through_fog
from design_scripts.core.player import compose_small_player
from design_scripts.templates.outlined_cutout_template import build_outlined_cutout
from examples.demo import create_demo

class TestReusableComponents(unittest.TestCase):
    def test_mask_multiplies_alpha(self):
        src=Image.new("RGBA",(20,20),(255,30,10,0))
        src.putpixel((10,10),(255,30,10,100))
        masked=apply_alpha_mask(src,Image.new("L",(20,20),128))
        self.assertEqual(masked.getpixel((2,2))[3],0)
        self.assertAlmostEqual(masked.getpixel((10,10))[3],50,delta=1)

    def test_outline_extends_outside_original_bounds(self):
        cut=Image.new("RGBA",(80,80),(0,0,0,0))
        ImageDraw.Draw(cut).ellipse((2,2,77,77),fill=(255,100,50,255))
        out=add_pencil_outline(cut,padding=20)
        self.assertEqual(out.size,(120,120))
        self.assertGreater(out.getpixel((19,60))[3],0)

    def test_fog_reveal_not_opaque_letters(self):
        clear=Image.new("RGBA",(300,200),(40,110,50,255))
        fog=Image.new("RGBA",(300,200),(210,210,200,255))
        mask=handwriting_mask((300,200),["Joy"],(30,25),font_size=80)
        result=reveal_through_fog(clear,fog,mask)
        self.assertEqual(result.getpixel((0,0))[:3],(210,210,200))
        self.assertNotEqual(result.getbbox(),None)
        self.assertTrue(any(p[:3]!=(210,210,200) for p in result.crop((30,30,250,150)).get_flattened_data()))

    def test_player_preserves_square_cover_crop(self):
        base=Image.new("RGBA",(500,800),(200,170,150,255))
        portrait=Image.new("RGB",(100,200),(30,140,90))
        card=compose_small_player(base,(80,70,420,650),portrait)
        self.assertEqual(card.size,base.size)
        self.assertNotEqual(card.getpixel((120,120)),base.getpixel((120,120)))

    def test_halo_stays_under_cutout(self):
        bg=Image.new("RGB",(320,480),(100,100,100))
        cut=Image.new("RGBA",(100,100),(0,0,0,0))
        ImageDraw.Draw(cut).rectangle((15,15,85,85),fill=(200,30,25,255))
        poster=build_outlined_cutout(bg,[(cut,(100,200))],size=(320,480))
        self.assertEqual(poster.getpixel((150,250))[:3],(200,30,25))

    def test_demo_three_pngs(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs=create_demo(Path(temp),size=(540,960))
            self.assertEqual(len(outputs),3)
            for file in outputs:
                with Image.open(file) as im:
                    self.assertEqual(im.size,(540,960))
                    self.assertEqual(im.format,"PNG")

if __name__=="__main__": unittest.main()
