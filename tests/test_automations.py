import unittest
from altissia_bot.automations import is_blacklisted, clean_text

class TestAutomations(unittest.TestCase):
    def test_is_blacklisted(self):
        self.assertTrue(is_blacklisted("Incorrect"))
        self.assertTrue(is_blacklisted("This is Wrong"))
        self.assertTrue(is_blacklisted("Please Select the right answer"))

        # Should not be blacklisted (partial match issues checked)
        self.assertFalse(is_blacklisted("Trustworthy")) # Contains "worthy", but no blacklist word
        self.assertFalse(is_blacklisted("The house is big"))

    def test_clean_text(self):
        self.assertEqual(clean_text('"Hello"'), "Hello")
        self.assertEqual(clean_text("Hello."), "Hello")
        self.assertEqual(clean_text("  Hello  "), "Hello")
