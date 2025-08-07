import requests
from bs4 import BeautifulSoup
from datetime import datetime


news_url = "https://timesofindia.indiatimes.com/"


try:
    response = requests.get(news_url, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(" Error fetching the website:", e)
    exit()

news_soup = BeautifulSoup(response.content, 'html.parser')


headlines = news_soup.find_all('h2', class_='title')

if not headlines:
    promo_anchors = news_soup.find_all('a', class_='promo-heading')
    headlines = [a for a in promo_anchors if a.text.strip()]

if not headlines:
    headlines = [
        a for a in news_soup.find_all('a', href=True)
        if "/news/" in a["href"] and a.text.strip()
    ]


if not headlines:
    print(" No headlines found.")
    exit()

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
file_name = "headlines_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"

with open(file_name, "w", encoding="utf-8") as f:
    f.write(f" Scraped on: {timestamp}\n")
    f.write("="*50 + "\n\n")
    for idx, headline in enumerate(headlines, 1):
        headline_text = headline.text.strip()
        print(f"{idx}. {headline_text}")
        f.write(f"{idx}. {headline_text}\n")

print(f"\n Headlines saved to '{file_name}'")
