#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import base64
import json
import datetime


def getNewsJson(data):
    return {
        'title': data.h3.a.text,
        'para': data.p.text,
        'href': data.a['href'],
        'img': 'data:image/png;base64, ' + base64.b64encode(requests.get(data.img['data-src']).content).decode('utf-8'),
        'img-src': data.img['data-src']
    }


URL = 'https://realty.economictimes.indiatimes.com/latest-news'

r = requests.get(URL)
soup = BeautifulSoup(r.content, 'html5lib')
dataItems = soup.find_all('li', {'data-recent-story': True})

newsDump = []
for news in dataItems:
    newsDump.append(getNewsJson(news))

with open('news.json', 'w') as outfile:
    now = datetime.datetime.now()
    date = {key: val for key, val in zip(['d', 'm', 'Y'], now.strftime('%d/%m/%Y').split("/"))}
    time = {key: val for key, val in zip(['H', 'M', 'S'], now.strftime('%H:%M:%S').split(":"))}
    json.dump({
        'updated_at': {
            'date': date,
            'time': time
        },
        'news': newsDump
    }, outfile)
