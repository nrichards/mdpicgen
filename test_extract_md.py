from unittest import TestCase

from util import extract_digit_ranges


class TestExtractButtonsFromMarkdown(TestCase):
    
    def test_extract_digit_ranges__single_digit(self):
        """Tests the function with a single digit string."""
        self.assert_extract_digit_ranges("5", "5")

    def test_extract_digit_ranges__hyphenated_range(self):
        """Tests the function with a hyphenated range."""
        self.assert_extract_digit_ranges("B1-8", "12345678")

    def test_extract_digit_ranges__non_alphanumeric(self):
        """Tests the function with a string containing non-alphanumeric characters."""
        self.assert_extract_digit_ranges("hello123-world[1-3, 7,8]", "12312378")

    def test_extract_digit_ranges__no_match(self):
        """Tests the function with a non-digit string."""
        self.assert_extract_digit_ranges("Sick - Kids - Like, Sleep", "")

    def assert_extract_digit_ranges(self, text, expected_output):
        actual_output = extract_digit_ranges(text)
        self.assertEqual(expected_output, actual_output)
