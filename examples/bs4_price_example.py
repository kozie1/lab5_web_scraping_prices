#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Przykład: pobieranie ceny z pojedynczej podstrony sklepu przy pomocy
# bibliotek requests oraz BeautifulSoup (bs4).
# Zakładamy, że produkt ma w HTML element:
#     <span class="product-price">123,45 zł</span> lub podobny.

import requests
from bs4 import BeautifulSoup

def fetch_product_price(url: str) -> float:
    # Wysyła żądanie HTTP GET i parsuje stronę
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    price_tag = soup.find("span", class_="product-price")
    if price_tag is None:
        raise ValueError(f"Nie znaleziono elementu z klasą 'product-price' w {url}")
    price_text = price_tag.get_text(strip=True)
    # Przetwarza np. "123,45 zł" → "123.45"
    numeric = price_text.replace(' ', '').replace('zł', '').replace('PLN', '')
    numeric = numeric.replace(',', '.').strip()
    try:
        return float(numeric)
    except ValueError:
        raise ValueError(f"Nie można sparsować ceny '{price_text}' do float")

if __name__ == "__main__":
    urls = [
        "https://example-shop.com/product/123",
        "https://example-shop.com/product/456"
    ]
    for url in urls:
        try:
            price = fetch_product_price(url)
            print(f"URL: {url}\n→ Cena: {price:.2f} zł\n")
        except Exception as e:
            print(f"URL: {url}\n→ Błąd: {e}\n")
