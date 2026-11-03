from __future__ import annotations

import unittest
from PIL import Image

from design_scripts.core.speckle import (
    grain_frosted_background, spray_reveal_mask, reveal_photo_in_spray_frost
)


class TestSprayFrost(unittest.TestCase):
    def setUp(self):
        self.photo = Image.new("RGB", (180, 260), (95, 137, 102))
        self.photo.paste((234, 150, 90), (40, 70, 140, 215))

    def test_reproducible_seed(self):
        a = grain_frosted_background(self.photo, seed=8)
        b = grain_frosted_background(self.photo, seed=8)
        self.assertEqual(a.tobytes(), b.tobytes())
        c = grain_frosted_background(self.photo, seed=9)
        self.assertNotEqual(a.tobytes(), c.tobytes())

    def test_mask_preserves_core_and_fogs_corners(self):
        mask = spray_reveal_mask((180, 260), (20, 45, 160, 230), edge_width=12, seed=4)
        self.assertEqual(mask.mode, "L")
        self.assertEqual(mask.getpixel((90, 130)), 255)
        self.assertEqual(mask.getpixel((0, 0)), 0)

    def test_composition_keeps_center_photo_pixel_exact(self):
        out = reveal_photo_in_spray_frost(self.photo, (20, 45, 160, 230), edge_width=12)
        self.assertEqual(out.getpixel((90, 130))[:3], self.photo.getpixel((90, 130)))
        self.assertEqual(out.size, self.photo.size)

    def test_bad_arguments_fail(self):
        with self.assertRaises(ValueError):
            spray_reveal_mask((40, 40), (5, 5, 30, 30), edge_width=0)
        with self.assertRaises(ValueError):
            grain_frosted_background(self.photo, grain_strength=2)


if __name__ == "__main__":
    unittest.main()
