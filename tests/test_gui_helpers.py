import unittest
from pathlib import Path

from pdf_splitter_gui import parse_drop_files


class ParseDropFilesTests(unittest.TestCase):
    def test_single_file(self):
        self.assertEqual(parse_drop_files('/tmp/a.pdf'), [Path('/tmp/a.pdf')])

    def test_braced_path_with_space(self):
        self.assertEqual(
            parse_drop_files('{/tmp/my file.pdf} {/tmp/b.pdf}'),
            [Path('/tmp/my file.pdf'), Path('/tmp/b.pdf')],
        )


if __name__ == '__main__':
    unittest.main()
