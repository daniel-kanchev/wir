import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from wir.items import Article


class WirSpider(scrapy.Spider):
    name = 'wir'
    start_urls = ['https://blog.wir.ch/']

    def parse(self, response):
        links = response.xpath('//a[@class="post-link"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="post-title padded-multiline"]/span/text()').get()
        if title:
            title = title.strip()

        date = " ".join(response.xpath('//div[@class="post-date minitext"]/text()').get().split()[2:])
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="ct-component ct-component-text"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
