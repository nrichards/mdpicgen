from unittest import TestCase

from imageset_gen import ImageSet, BG_LAYER_NAME


class TestImageSet(TestCase):
    def test_process_basename__single(self):
        actual_output = (
            ImageSet.layer_names_from_basename(basename="big", add_bg=True, unpack_digits=True))
        self.assertEqual([BG_LAYER_NAME, "big"], actual_output)

    def test_process_basename__multi_unpack_digits(self):
        actual_output = (
            ImageSet.layer_names_from_basename(basename="big_barf_123_wilt_234_5", add_bg=True, unpack_digits=True))
        self.assertEqual([BG_LAYER_NAME, "big", "barf", "1", "2", "3", "wilt", "2", "3", "4", "5"], actual_output)

    def test_process_basename__multi_no_unpack_digits(self):
        actual_output = (
            ImageSet.layer_names_from_basename(basename="big_barf_123_wilt_234_5", add_bg=True, unpack_digits=False))
        self.assertEqual([BG_LAYER_NAME, "big", "barf", "123", "wilt", "234", "5"], actual_output)
