import unittest

from pdf_splitter import build_ranges, parse_split_points


class ParseSplitPointsTests(unittest.TestCase):
    def test_parse_split_points_deduplicates_and_sorts(self):
        self.assertEqual(parse_split_points("5,3,5", 10), [3, 5])

    def test_parse_split_points_rejects_out_of_bounds(self):
        with self.assertRaises(ValueError):
            parse_split_points("10", 10)


class BuildRangesTests(unittest.TestCase):
    def test_build_ranges_without_overlap(self):
        self.assertEqual(build_ranges(10, [3, 5], overlap=False), [(0, 3), (3, 5), (5, 10)])

    def test_build_ranges_with_overlap(self):
        self.assertEqual(build_ranges(10, [3, 5], overlap=True), [(0, 3), (2, 5), (4, 10)])


if __name__ == "__main__":
    unittest.main()
