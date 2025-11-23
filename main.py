#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import base64
import json
import datetime


HOST_URL = "https://realty.economictimes.indiatimes.com"
SCRAPE_URL = HOST_URL + "/latest-news"


def getNewsJson(data):
    return {
        "title": data.h3.text,
        "para": data.p.text,
        "href": HOST_URL + data.a["href"],
        "img": "data:image/png;base64, "
        + base64.b64encode(requests.get(data.img["data-src"]).content).decode("utf-8"),
        "img-src": data.img["data-src"],
        "tag": data.a["href"].split("/")[2],
    }


r = requests.get(SCRAPE_URL)
soup = BeautifulSoup(r.content, "html5lib")
dataItems = soup.find_all("article", {"class": "desc"})

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
        newsDump.append(getNewsJson(news))
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
