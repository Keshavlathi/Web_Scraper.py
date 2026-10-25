import re
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup


NEWS_URL = "https://timesofindia.indiatimes.com/"


def normalize_headline(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    cleaned = re.sub(r"^(?:News|Live|Video|Analysis)\s+", "", cleaned, flags=re.IGNORECASE)
    return cleaned


def extract_headlines(soup: BeautifulSoup) -> List[str]:
    headlines: List[str] = []
    seen = set()
    selectors = ["h2.title", "h3.title", ".promo-heading", "a[href*='/news/']"]

    for selector in selectors:
        for element in soup.select(selector):
            headline_text = normalize_headline(element.get_text(" ", strip=True))
            if headline_text and headline_text not in seen:
                seen.add(headline_text)
                headlines.append(headline_text)

    if not headlines:
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "")
            headline_text = normalize_headline(anchor.get_text(" ", strip=True))
            if "/news/" in href and headline_text and headline_text not in seen:
                seen.add(headline_text)
                headlines.append(headline_text)

    return headlines


def fetch_news_page(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Error fetching the website: {exc}") from exc


def save_headlines(headlines: List[str]) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = "headlines_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(f"Scraped on: {timestamp}\n")
        file.write("=" * 50 + "\n\n")
        for idx, headline in enumerate(headlines, 1):
            print(f"{idx}. {headline}")
            file.write(f"{idx}. {headline}\n")

    return file_name


def main() -> int:
    try:
        html = fetch_news_page(NEWS_URL)
    except RuntimeError as exc:
        print(exc)
        return 1

    news_soup = BeautifulSoup(html, "html.parser")
    headlines = extract_headlines(news_soup)

    if not headlines:
        print("No headlines found.")
        return 1

    file_name = save_headlines(headlines)
    print(f"\nHeadlines saved to '{file_name}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
