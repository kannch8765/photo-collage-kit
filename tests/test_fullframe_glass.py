"""Full-frame frost stays a pure filter, not a collage/compositing step."""
import unittest
from PIL import Image, ImageDraw

from design_scripts.core.speckle import full_frame_spray_frost


class TestFullFrameSprayFrost(unittest.TestCase):
    def setUp(self):
        self.input = Image.new("RGB", (180, 260), (105, 82, 74))
        d = ImageDraw.Draw(self.input)
        d.ellipse((35, 60, 150, 210), fill=(232, 176, 86))
        d.rectangle((14, 14, 75, 42), fill=(75, 130, 96))

    def test_fullframe_output_retains_dimensions_and_source(self):
        before = self.input.tobytes()
        result = full_frame_spray_frost(self.input)
        self.assertEqual(result.size, self.input.size)
        self.assertEqual(result.mode, "RGBA")
        self.assertEqual(before, self.input.tobytes())

    def test_seed_is_reproducible(self):
        first = full_frame_spray_frost(self.input, seed=123)
        second = full_frame_spray_frost(self.input, seed=123)
        different = full_frame_spray_frost(self.input, seed=124)
        self.assertEqual(first.tobytes(), second.tobytes())
        self.assertNotEqual(first.tobytes(), different.tobytes())

    def test_strength_is_decoupled_from_blur(self):
        smooth = full_frame_spray_frost(self.input, grain_strength=0)
        speckled = full_frame_spray_frost(self.input, grain_strength=0.8)
        self.assertNotEqual(smooth.tobytes(), speckled.tobytes())
        self.assertEqual(speckled.getchannel("A").getextrema(), (255, 255))

    def test_bad_arguments(self):
        with self.assertRaises(ValueError):
            full_frame_spray_frost(self.input, blur_radius=-1)
        with self.assertRaises(ValueError):
            full_frame_spray_frost(self.input, grain_strength=1.2)
        with self.assertRaises(ValueError):
            full_frame_spray_frost(self.input, mist_strength=-.1)


if __name__ == "__main__":
    unittest.main()
