# -*- coding: utf-8 -*-

BOT_NAME = "scrapy_price_example"

SPIDER_MODULES = ["myprices.spiders"]
NEWSPIDER_MODULE = "myprices.spiders"

# Respektuj robots.txt
ROBOTSTXT_OBEY = True

# Liczba równoległych żądań (domyślnie 8)
CONCURRENT_REQUESTS = 8

# Opóźnienie między żądaniami (sekundy)
DOWNLOAD_DELAY = 1.0

# Domyślne ustawienie eksportu (można nadpisać przy uruchomieniu spidera):
# FEED_FORMAT = "json"
# FEED_URI = "prices.json"
