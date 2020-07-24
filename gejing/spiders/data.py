# -*- coding: utf-8 -*-
import scrapy
from gejing.items import GejingItem

class DataSpider(scrapy.Spider):
    name = 'data'
    allowed_domains = ['cnki.com.cn']
    start_urls = ['http://cnki.com.cn/']

    def __init__(self):
        self.page = 1
        self.post_url = 'http://search.cnki.com.cn/Search/Result'


    def start_requests(self):
        # post_url = "http://search.cnki.com.cn/Search/Result"
        data = {
            "searchType": "MulityTermsSearch",
            "Content": "个人数据",
        }

        yield scrapy.FormRequest(url=self.post_url, formdata=data, callback=self.parse)

    def parse(self, response):

        #一共有多少条数据15787
        #total_count = response.xpath('//input[@class="pTotalCount"]/@value').extract_first()

        # 每一页有20条，共计790
        # total_page = int(int(total_count)/20) + 1
        total_page = 790

        div_list = response.xpath("//div[@class='list-item']")

        for div in div_list:
            item = GejingItem()
            title = div.xpath("./p/a[@class='left']/@title").extract_first()
            # abstract = div.xpath('./p[@class="nr"]/text()').extract()
            abstract_xpath = div.xpath('./p[@class="nr"]')
            abstract = abstract_xpath.xpath('string(.)').extract_first()
            words = div.xpath("./div/p[@class='info_left left']/a/text()").extract()
            download = div.xpath("./div/p[@class='info_right right']/span[1]/text()").extract_first()
            quote = div.xpath("./div/p[@class='info_right right']/span[2]/text()").extract_first()
            source_list = div.xpath('./p[@class="source"]')
            for source in source_list:
                paper_type = source.xpath("./span[last()]/text()").extract_first()
                if paper_type == "期刊":
                    teacher = ""
                    author = source.xpath("./span[1]/@title").extract_first()
                    paper_source = source.xpath("./a[1]/span/text()").extract_first()
                    date = source.xpath("./a[2]/span/text()").extract_first()
                else:
                    author = source.xpath("./span[1]/@title").extract_first()
                    teacher = source.xpath("./span[2]/a/text()").extract_first()
                    paper_source = source.xpath("./span[3]/text()").extract_first()
                    date = source.xpath("./span[4]/text()").extract_first()

                item['title'] = title
                item['abstract'] = abstract
                item['words'] = ' '.join(words)
                item['download'] = download
                item['quote'] = quote
                item['paper_type'] = paper_type
                item['teacher'] = teacher
                item['author'] = author
                item['paper_source'] = paper_source
                item['date'] = date

                print(item)
                # yield item


        if self.page < total_page:
            self.page += 1
            data = {
                "searchType": "MulityTermsSearch",
                "Content": "个人数据",
                "ParamIsNullOrEmpty": "false",
                "Islegal": "false",
                "Order": "1",
                "Page": str(self.page)
            }
            yield scrapy.FormRequest(url=self.post_url, formdata=data, callback=self.parse)

