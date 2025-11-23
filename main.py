#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import base64
import json
import datetime
import time


HOST_URL = "https://realty.economictimes.indiatimes.com"
SCRAPE_URL = HOST_URL + "/latest-news"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}


def getNewsJson(data, session):
    return {
        "title": data.h3.text,
        "para": data.p.text,
        "href": HOST_URL + data.a["href"],
        "img": "data:image/png;base64, "
        + base64.b64encode(session.get(data.img["data-src"], headers=HEADERS, timeout=10).content).decode("utf-8"),
        "img-src": data.img["data-src"],
        "tag": data.a["href"].split("/")[2],
    }


session = requests.Session()
time.sleep(2)

try:
    r = session.get(SCRAPE_URL, headers=HEADERS, timeout=10)
    r.raise_for_status()
    
    print(f"Response status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print(f"Content-Encoding: {r.headers.get('Content-Encoding')}")
    print(f"Response encoding detected: {r.encoding}")
    
    r.encoding = 'utf-8'
    html_content = r.text
    
    print(f"Response length: {len(html_content)} characters")
    
except Exception as e:
    print(f"Request failed: {e}")
    raise

soup = BeautifulSoup(html_content, "html5lib")

if "Access Denied" in soup.text or "access denied" in soup.text.lower():
    print("Still getting blocked. Response preview:")
    print(soup.text[:500])
    raise Exception("Access denied by the website")

dataItems = soup.find_all("article", {"class": "desc"})
print(f"Found {len(dataItems)} article items")

if len(dataItems) == 0:
    print("\nNo articles found. Let's inspect the HTML structure...")
    print("First 2000 characters of the page:")
    print(soup.prettify()[:2000])
    print("\n\nSearching for any articles:")
    all_articles = soup.find_all("article")
    print(f"Total article tags found: {len(all_articles)}")
    if all_articles:
        for i, art in enumerate(all_articles[:3]):
            print(f"\nArticle {i+1} classes: {art.get('class')}")
            print(f"Article {i+1} preview: {str(art)[:200]}")

now = datetime.datetime.now()
date = {
    key: val for key, val in zip(["d", "m", "Y"], now.strftime("%d/%m/%Y").split("/"))
}
time = {
    key: val for key, val in zip(["H", "M", "S"], now.strftime("%H:%M:%S").split(":"))
}

newsDump = []
for news in dataItems:
    try:
        newsDump.append(getNewsJson(news, session))
    except:
        pass

if len(newsDump) < 3:
    raise Exception("Failed to load enough data for pristine group news api!")

with open("news.json", "w") as outfile:
    json.dump({"updated_at": {"date": date, "time": time}, "news": newsDump}, outfile)

with open("news-top.json", "w") as outfile:
    json.dump(
        {"updated_at": {"date": date, "time": time}, "news": newsDump[:3]}, outfile
    )
