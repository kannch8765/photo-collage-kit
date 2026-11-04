"""Render/alpha regression checks for original journal stickers."""
import unittest
from PIL import Image
from design_scripts.core.sticker_doodles import NAMES, render_doodle, paste_doodle


class StickerDoodleTests(unittest.TestCase):
    def test_all_icons_transparent_and_resized(self):
        for name in NAMES:
            with self.subTest(name=name):
                icon=render_doodle(name,96)
                self.assertEqual(icon.size,(96,96))
                self.assertEqual(icon.mode,"RGBA")
                alpha=icon.getchannel("A")
                self.assertEqual(alpha.getpixel((0,0)),0)
                self.assertIsNotNone(alpha.getbbox())

    def test_reject_invalid_name_and_size(self):
        with self.assertRaises(ValueError): render_doodle("unicorn")
        with self.assertRaises(ValueError): render_doodle("heart",8)

    def test_paste_does_not_modify_input(self):
        img=Image.new("RGB",(180,180),(255,255,255))
        result=paste_doodle(img,"sakura",(90,90),60,rotation=12)
        self.assertEqual(img.getpixel((90,90)),(255,255,255))
        self.assertNotEqual(result.getpixel((90,90)),(255,255,255,255))

if __name__=="__main__": unittest.main()
