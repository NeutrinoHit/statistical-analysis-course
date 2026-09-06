"""Regression checks for chapter boundaries, page labels and spreads."""

import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from render_book_chapters import Chapter, chapter_end_pages, extract_chapter


class ChapterBoundariesTest(unittest.TestCase):
    def setUp(self):
        self.chapters = [
            Chapter("01_first", "First", Path("01_first.qmd")),
            Chapter("02_second", "Second", Path("02_second.qmd")),
            Chapter("03_third", "Third", Path("03_third.qmd")),
        ]

    def test_parts_and_back_cover_are_excluded(self):
        pages = {"Part I": 3, "First": 4, "Second": 10, "Part II": 16, "Third": 17}
        self.assertEqual(
            chapter_end_pages(self.chapters, pages, ["Part I", "Part II"], 25),
            {"01_first": 10, "02_second": 16, "03_third": 25},
        )

    def test_book_without_parts_uses_physical_page_order(self):
        self.assertEqual(
            chapter_end_pages(list(reversed(self.chapters)), {"First": 2, "Second": 9, "Third": 14}, [], 20),
            {"01_first": 9, "02_second": 14, "03_third": 20},
        )

    def test_missing_part_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "Missing part"):
            chapter_end_pages(self.chapters, {"First": 2, "Second": 9, "Third": 14}, ["Missing part"], 20)

    def test_chapter_after_content_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "Third"):
            chapter_end_pages(self.chapters, {"First": 2, "Second": 9, "Third": 20}, [], 20)


class ChapterPaginationTest(unittest.TestCase):
    def test_labels_and_opening_side_survive_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "book.pdf"
            output = Path(directory) / "chapter.pdf"
            writer = PdfWriter()
            for _ in range(5):
                writer.add_blank_page(width=595, height=842)
            writer.set_page_label(0, 1, style="/r", start=1)
            writer.set_page_label(2, 4, style="/D", start=1)
            writer.write(source)

            for start, expected, layout in (
                (2, ["1", "2", "3"], "/TwoPageRight"),
                (3, ["2", "3"], "/TwoPageLeft"),
                (1, ["ii", "1", "2", "3"], "/TwoPageLeft"),
            ):
                with self.subTest(start=start):
                    extract_chapter(source, output, "Chapter", "Author", "Subject", start, 5)
                    reader = PdfReader(output)
                    self.assertEqual(reader.page_labels, expected)
                    self.assertEqual(reader.page_layout, layout)
                    self.assertGreaterEqual(reader.pdf_header, "%PDF-1.5")
                    self.assertEqual(len(reader.pages), 5 - start)
                    self.assertEqual(reader.outline[0].title, "Chapter")


if __name__ == "__main__":
    unittest.main()
