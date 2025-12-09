import unittest
from altissia_bot.utils import is_color_green

class TestColorDetection(unittest.TestCase):
    def test_green_colors(self):
        # Explicit greens
        self.assertTrue(is_color_green("rgb(34, 197, 94)"))
        self.assertTrue(is_color_green("rgb(22, 163, 74)"))
        self.assertTrue(is_color_green("rgba(0, 128, 0, 1)"))

        # Light greens (backgrounds)
        self.assertTrue(is_color_green("rgb(233, 251, 241)"))

    def test_non_green_colors(self):
        # Red
        self.assertFalse(is_color_green("rgb(255, 0, 0)"))
        # Blue
        self.assertFalse(is_color_green("rgb(0, 0, 255)"))
        # White
        self.assertFalse(is_color_green("rgb(255, 255, 255)"))
        # Black
        self.assertFalse(is_color_green("rgb(0, 0, 0)"))

    def test_invalid_input(self):
        self.assertFalse(is_color_green(""))
        self.assertFalse(is_color_green("invalid"))
        self.assertFalse(is_color_green("rgb(20, 20)")) # Missing blue
