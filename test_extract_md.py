from unittest import TestCase

from extract_md import ExtractButtonsFromMarkdown


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

    def test_extract_digit_ranges__first_capture_group(self):
        """Tests the function with a capture group excluding unwanted decorative digits."""
        self.assert_extract_digit_ranges("B[1-8] (2nd pattern) in any sub-mode", "12345678")

    def assert_extract_digit_ranges(self, text, expected_output):
        actual_output = ExtractButtonsFromMarkdown.extract_digit_ranges(text)
        self.assertEqual(actual_output, expected_output)
