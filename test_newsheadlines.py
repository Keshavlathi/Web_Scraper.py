import csv
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from newsheadlines import (
    SOURCES,
    extract_headlines,
    normalize_headline,
    save_headlines,
)


class HeadlineExtractionTests(unittest.TestCase):
    def test_extracts_and_deduplicates_times_of_india_articles(self) -> None:
        html = """
        <a href="/india/story/articleshow/123.cms?from=home">
            <h2>News A headline from Times of India</h2>
        </a>
        <a href="/india/story/articleshow/123.cms">
            <h2>News A headline from Times of India</h2>
        </a>
        <a href="/city/aurangabad">City page</a>
        <a href="/sports/cricket/live-cricket-score">
            <h2>Cricket Live Score</h2>
        </a>
        <a href="https://example.com/india/story/articleshow/456.cms">
            <h2>External article title that should not be included</h2>
        </a>
        """

        headlines = extract_headlines(
            BeautifulSoup(html, "html.parser"), SOURCES[0]
        )

        self.assertEqual(len(headlines), 1)
        self.assertEqual(headlines[0].source, "Times of India")
        self.assertEqual(headlines[0].title, "A headline from Times of India")
        self.assertEqual(
            headlines[0].url,
            "https://timesofindia.indiatimes.com/india/story/articleshow/123.cms",
        )

    def test_extracts_hindustan_times_article_links(self) -> None:
        html = """
        <a href="/india-news/story-title-101234567890123.html">
            <h3>A current Hindustan Times headline</h3>
        </a>
        <a href="/india-news">India news section</a>
        <a href="/india-news/not-an-article.html">
            <h3>Page without article id does not count</h3>
        </a>
        """

        headlines = extract_headlines(
            BeautifulSoup(html, "html.parser"), SOURCES[1]
        )

        self.assertEqual(len(headlines), 1)
        self.assertEqual(headlines[0].source, "Hindustan Times")
        self.assertEqual(headlines[0].title, "A current Hindustan Times headline")
        self.assertTrue(headlines[0].url.endswith("-101234567890123.html"))

    def test_normalizes_whitespace_and_category_prefix(self) -> None:
        self.assertEqual(
            normalize_headline("  News   A headline \n from the homepage "),
            "A headline from the homepage",
        )

    def test_saves_source_and_article_details_as_csv(self) -> None:
        html = """
        <a href="/india-news/story-title-101234567890123.html">
            <h3>A current Hindustan Times headline</h3>
        </a>
        """
        headlines = extract_headlines(
            BeautifulSoup(html, "html.parser"), SOURCES[1]
        )

        with tempfile.TemporaryDirectory() as temporary_dir:
            output_path = save_headlines(headlines, Path(temporary_dir))
            with output_path.open(encoding="utf-8-sig", newline="") as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source"], "Hindustan Times")
        self.assertEqual(rows[0]["title"], "A current Hindustan Times headline")
        self.assertTrue(rows[0]["url"].startswith("https://www.hindustantimes.com/"))
        self.assertTrue(rows[0]["fetched_at"])


if __name__ == "__main__":
    unittest.main()
