# Lab 5 – Zbieranie Danych i Monitorowanie Cen w Pythonie

## 1. Wprowadzenie
Celem tego laboratorium jest:
1. **Poznanie i ocena** dwóch bibliotek Python służących do pobierania (scrapowania) danych ze stron internetowych.  
2. **Praktyczna demonstracja** – przygotowanie krótkich przykładów pokazujących, jak w praktyce wyciągnąć cenę produktu ze sklepu internetowego.  
3. **Dokumentacja i repozytorium** – umieszczenie skryptów wraz z komentarzami oraz raportu w pliku `README.md` na GitHub.

Wybrane biblioteki:
- **Requests + BeautifulSoup** – lekki zestaw do jednokrotnego pobierania i parsowania stron HTML.
- **Scrapy** – zaawansowany framework do crawlowania wielu stron, paginacji i efektywnego zbierania większej liczby danych.

Domena zastosowania: **zbieranie informacji o cenach produktów** z witryn e-commerce, zaś w przyszłości porównywanie ich w czasie w celu monitorowania promocji i analiz rynkowych.

---

## 2. Biblioteki Python i ich charakterystyka

### 2.1. Requests + BeautifulSoup (bs4)

- **Przeznaczenie**:  
  - `requests` – wysyłanie żądań HTTP (GET/POST) do dowolnej strony www.  
  - `BeautifulSoup` – parsowanie kodu HTML/XML, wygodne wyszukiwanie elementów po tagach, klasach lub selektorach CSS.

- **Główne zalety**:
  1. **Prostota użycia** – minimalna konfiguracja, szybko można napisać prosty skrypt do wyciągania kilku elementów.  
  2. **Niewielkie zależności** – wystarczy tylko zainstalować dwa pakiety.  
  3. **Elastyczność** – można używać dowolnych selektorów (CSS lub XPath), swobodnie modyfikować kod HTML przed parsowaniem.

- **Ograniczenia**:
  1. **Brak wbudowanej obsługi paginacji** – ręcznie trzeba w pętli generować kolejne URL-e i wywoływać funkcję do pobrania ceny.  
  2. **Brak asynchroniczności** – każde żądanie jest synchroniczne (blokujące), co przy większej liczbie URL-i może być wolne.  
  3. **Nie nadaje się do skomplikowanych struktur** typu strony mocno opartych na JavaScript (bez dodatkowego silnika do renderowania JS).

- **Przykładowy kod**:  
  Plik: `examples/bs4_price_example.py`  
  ```python
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
  ```

- **Linki do dokumentacji**:  
  - BeautifulSoup (bs4): https://www.crummy.com/software/BeautifulSoup/bs4/doc/  
  - Requests: https://docs.python-requests.org/

---

### 2.2. Scrapy

- **Przeznaczenie**:  
  Pełnoprawny framework do web crawling-u i scrapowania. Pozwala na asynchroniczne wykonywanie wielu żądań, automatyczne podążanie za linkami (paginacja), przetwarzanie danych przez pipeline’y i eksport do różnych formatów (JSON, CSV, XML).  

- **Główne zalety**:
  1. **Wydajność** – dzięki wbudowanej asynchroniczności (Twisted) i zarządzaniu kolejkami żądań, scrapowanie setek czy tysięcy podstron jest znacząco szybsze.  
  2. **Modularność** – można dodać własne middleware, pipeline’y do czyszczenia lub zapisywania danych.  
  3. **Automatyczne podążanie za linkami** – wystarczy w kodzie spidra opisać selektor do elementu „następna strona” i Scrapy zajmie się resztą.  
  4. **Bogate możliwości eksportu** – łatwy zapis do pliku JSON, CSV lub bazy danych.

- **Ograniczenia**:
  1. **Krzywa uczenia się** – na początku trzeba poznać strukturę projektu Scrapy (settings, items, spiders, pipelines).  
  2. **Większa konfiguracja** – nawet prosty spider wymaga utworzenia projektu, plików `settings.py`, `items.py` itd.  
  3. **Duże zależności** – biblioteka Scrapy waży więcej i wymaga kilku dodatkowych pakietów (Twisted itp.).

- **Przykładowy kod (spider)**:  
  Plik: `examples/scrapy_price_example/myprices/spiders/prices_spider.py`  
  ```python
  import scrapy
  from myprices.items import ProductPriceItem

  class PricesSpider(scrapy.Spider):
      name = "prices"
      allowed_domains = ["example-shop.com"]
      start_urls = [
          "https://example-shop.com/sklep?page=1",
      ]

      def parse(self, response):
          product_blocks = response.css("div.product")
          for prod in product_blocks:
              item = ProductPriceItem()
              item["name"] = prod.css("h2.product-title::text").get().strip()
              price_text = prod.css("span.product-price::text").get().strip()
              numeric = price_text.replace(' ', '').replace('zł', '').replace('PLN', '').replace(',', '.').strip()
              try:
                  item["price"] = float(numeric)
              except ValueError:
                  item["price"] = None
              href = prod.css("a::attr(href)").get()
              if href:
                  item["url"] = response.urljoin(href)
              else:
                  item["url"] = response.url
              yield item

          next_page = response.css("a.next-page::attr(href)").get()
          if next_page:
              yield response.follow(next_page, callback=self.parse)
  ```

- **Linki do dokumentacji**:  
  - Scrapy: https://docs.scrapy.org/  
  - PyPI Scrapy: https://pypi.org/project/Scrapy/

---

## 3. Instalacja i uruchomienie przykładów

### 3.1. Utworzenie i aktywacja wirtualnego środowiska

```bash
python3 -m venv venv
source venv/bin/activate       # Linux/macOS
# venv\\Scripts\\activate   # Windows PowerShell
```

### 3.2. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 3.3. Uruchomienie przykładu Requests + BeautifulSoup

```bash
python examples/bs4_price_example.py
```
- Skrypt wypisze cenę (lub błąd, jeśli nie znajdzie elementu `span.product-price`) dla podanych adresów URL.

### 3.4. Uruchomienie przykładu Scrapy

1. Przejdź do katalogu projektu Scrapy:
   ```bash
   cd examples/scrapy_price_example
   ```
2. Uruchom spidera (w tym przykładzie zapisujemy wynik w `prices.json` w katalogu `examples`):
   ```bash
   scrapy crawl prices -o ../prices.json
   ```
3. Po zakończeniu działania znajdziesz w `examples/prices.json` plik JSON z listą wszystkich `name` i `price` dla produktów napotkanych podczas crawl-owania.

---

## 4. Cele i kryteria oceny

1. **Wybór dwóch bibliotek**:  
   - Requests + BeautifulSoup  
   - Scrapy  

2. **Demonstracja działania**:  
   - Przykładowy skrypt (`bs4_price_example.py`) pokazuje, jak pobrać i sparsować cenę z pojedynczego URL.  
   - Projekt Scrapy (`prices_spider.py`) pokazuje automatyczne przechodzenie przez kolejne strony sklepu, zbieranie nazwy i ceny oraz eksport do formatu JSON.

3. **Instalacja i konfiguracja**:  
   - Wirtualne środowisko  
   - Plik `requirements.txt` z bibliotekami  
   - README opisujący kroki

4. **Dokumentacja i raport**:  
   - Ten plik `README.md` zawiera opis bibliotek, ich zalety, ograniczenia, linki do dokumentacji oraz instrukcje uruchomienia.  
   - Skrypty zawierają komentarze wyjaśniające (#) na temat działania funkcji i selektorów.

5. **Struktura repozytorium**:  
   - Czytelne rozmieszczenie plików w katalogach (`examples/`, `scrapy_price_example/`).  
   - Folder `examples/scrapy_price_example` zawiera cały projekt Scrapy, a w jego wnętrzu katalog `myprices` z modułami.

---

## 5. Podsumowanie

Dzięki powyższym przykładom pokazujemy, w jaki sposób:

- Szybko i prosto (Requests + BeautifulSoup) pozyskać cenę ze statycznej podstrony sklepu.  
- Efektywnie i skalowalnie (Scrapy) przejść przez wiele podstron (paginację), zebrać duży zbiór danych o cenach i zapisać do pliku JSON.  

Oba podejścia pozwalają na zbieranie danych do dalszej analizy (np. porównywanie cen w czasie) oraz monitorowanie promocji. W zależności od skali zadania możesz użyć prostego skryptu lub wdrożyć pełny crawler z pipeline’ami. 

Możesz rozpoczynać integrację z systemem monitorującym, zapisywać wyniki do bazy (np. SQLite, PostgreSQL) lub eksportować dane do plików CSV/JSON — to już kolejny krok w rozwinięciu projektu.

---

## 6. Linki do dokumentacji

- **BeautifulSoup (bs4)**:  
  https://www.crummy.com/software/BeautifulSoup/bs4/doc/  

- **Requests**:  
  https://docs.python-requests.org/  

- **Scrapy**:  
  https://docs.scrapy.org/en/latest/  

---

### Licencja, autor, data

- **Autor**: [Twoje Imię i Nazwisko]  
- **Data wykonania**: 2025-06-01  
- **Licencja**: MIT (opcjonalnie)
