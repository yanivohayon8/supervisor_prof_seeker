# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
# from w3lib.html import remove_tags
from itemloaders.processors import TakeFirst


class SupervisorItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    personal_website_url = scrapy.Field()