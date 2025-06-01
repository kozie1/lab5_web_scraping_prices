import scrapy
from myprices.items import ProductPriceItem

class PricesSpider(scrapy.Spider):
    """
    Przykładowy Spider, który odwiedza podstrony sklepu i zbiera nazwy produktów oraz ceny.
    Zakładamy uproszczoną strukturę HTML:
      <div class="product">
        <h2 class="product-title">Nazwa produktu</h2>
        <span class="product-price">123,45 zł</span>
      </div>
    oraz paginację:
      <a class="next-page" href="/sklep?page=2">Następna</a>
    """
    name = "prices"
    allowed_domains = ["example-shop.com"]
    start_urls = [
        "http://books.toscrape.com",
    ]

    def parse(self, response):
        """
        Dla każdej strony sklepu:
        - Znajdź wszystkie bloki <div class="product">
        - Wyciągnij nazwę i cenę
        - Przejdź do kolejnej strony ('next-page')
        """
        # 1. Selektor elementów produktów
        product_blocks = response.css("div.product")

        for prod in product_blocks:
            item = ProductPriceItem()
            # Wyciągamy nazwę produktu (tag h2 z klasą 'product-title')
            item["name"] = prod.css("h2.product-title::text").get().strip()
            # Wyciągamy tekst z <span class="product-price"> i konwertujemy na float
            price_text = prod.css("span.product-price::text").get().strip()
            # Przetwarzamy np. "123,45 zł" → "123.45"
            numeric = price_text.replace(' ', '').replace('zł', '').replace('PLN', '')
            numeric = numeric.replace(',', '.').strip()
            try:
                item["price"] = float(numeric)
            except ValueError:
                item["price"] = None  # lub zadeklaruj w jakiś inny sposób
            href = prod.css("a::attr(href)").get()
            if href:
                item["url"] = response.urljoin(href)
            else:
                item["url"] = response.url

            yield item

        # 2. Obsługa paginacji: jeśli jest link do kolejnej strony, follow()
        next_page = response.css("a.next-page::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
