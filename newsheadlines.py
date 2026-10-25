import csv
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class NewsSource:
    name: str
    url: str
    domain: str

    def is_article_url(self, url: str) -> bool:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if hostname != self.domain and not hostname.endswith("." + self.domain):
            return False

        path = parsed.path.lower()
        if self.name == "Times of India":
            path_parts = [part for part in path.split("/") if part]
            return "/articleshow/" in path or (
                len(path_parts) >= 3
                and len(path_parts[-1]) >= 25
                and path.startswith(
                    ("/india/", "/world/", "/business/", "/technology/",
                     "/sports/", "/education/", "/entertainment/", "/city/")
                )
            )

        return bool(re.search(r"-\d+\.html$", path))


@dataclass(frozen=True)
class Headline:
    source: str
    title: str
    url: str
    fetched_at: str


SOURCES = (
    NewsSource(
        name="Times of India",
        url="https://timesofindia.indiatimes.com/",
        domain="timesofindia.indiatimes.com",
    ),
    NewsSource(
        name="Hindustan Times",
        url="https://www.hindustantimes.com/",
        domain="hindustantimes.com",
    ),
)


def normalize_headline(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    return re.sub(
        r"^(?:News|Live|Video|Analysis)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )


def extract_headlines(soup: BeautifulSoup, source: NewsSource) -> List[Headline]:
    fetched_at = datetime.now().astimezone().isoformat(timespec="seconds")
    headlines: List[Headline] = []
    seen_urls = set()

    for anchor in soup.find_all("a", href=True):
        url = urldefrag(urljoin(source.url, anchor["href"]))[0]
        parsed_url = urlparse(url)
        url = parsed_url._replace(query="").geturl()
        if not source.is_article_url(url):
            continue

        title_element = anchor.find(["h1", "h2", "h3", "h4"])
        title = normalize_headline(
            title_element.get_text(" ", strip=True)
            if title_element
            else anchor.get_text(" ", strip=True)
        )
        if len(title) < 15 or url in seen_urls:
            continue

        seen_urls.add(url)
        headlines.append(
            Headline(
                source=source.name,
                title=title,
                url=url,
                fetched_at=fetched_at,
            )
        )

    return headlines


def fetch_news_page(source: NewsSource) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(source.url, timeout=20, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"{source.name}: error fetching the website: {exc}") from exc


def scrape_source(source: NewsSource) -> List[Headline]:
    html = fetch_news_page(source)
    headlines = extract_headlines(BeautifulSoup(html, "html.parser"), source)
    if not headlines:
        raise RuntimeError(
            f"{source.name}: no article headlines found; the site's page layout may have changed."
        )
    return headlines


def save_headlines(headlines: List[Headline], output_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = output_dir / f"headlines_{timestamp}.csv"
    fieldnames = ["source", "title", "url", "fetched_at"]

    with file_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for headline in headlines:
            writer.writerow(
                {
                    "source": headline.source,
                    "title": headline.title,
                    "url": headline.url,
                    "fetched_at": headline.fetched_at,
                }
            )

    return file_path


def main() -> int:
    all_headlines: List[Headline] = []
    failed_sources = []

    for source in SOURCES:
        try:
            headlines = scrape_source(source)
        except RuntimeError as exc:
            print(exc, file=sys.stderr)
            failed_sources.append(source.name)
            continue

        all_headlines.extend(headlines)
        print(f"{source.name}: found {len(headlines)} headlines")

    if not all_headlines:
        print("No headlines were collected from either news site.", file=sys.stderr)
        return 1

    try:
        file_path = save_headlines(all_headlines, Path(__file__).resolve().parent)
    except OSError as exc:
        print(f"Error saving headlines: {exc}", file=sys.stderr)
        return 1

    print(f"Saved {len(all_headlines)} headlines to '{file_path.name}'")
    if failed_sources:
        print(
            "Results are incomplete; failed sources: "
            + ", ".join(failed_sources),
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
