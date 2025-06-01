import scrapy

class ProductPriceItem(scrapy.Item):
    # Pole z nazwą produktu
    name = scrapy.Field()
    # Pole z ceną (float)
    price = scrapy.Field()
    # Opcjonalnie: URL produktu
    url = scrapy.Field()
