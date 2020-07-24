# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GejingItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    abstract = scrapy.Field()
    words = scrapy.Field()
    download = scrapy.Field()
    quote = scrapy.Field()
    author = scrapy.Field()
    teacher = scrapy.Field()
    paper_source = scrapy.Field()
    date = scrapy.Field()
    paper_type = scrapy.Field()

