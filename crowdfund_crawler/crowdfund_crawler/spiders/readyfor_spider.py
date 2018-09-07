import scrapy

class ReadyforSpider(scrapy.Spider):
    name="readyfor_spider"
    start_urls = ['https://readyfor.jp/tags/charity']

    def parse(self,response):
        for url in response.xpath("//a[name(..)='article']/@href").extract():
            yield scrapy.Request(response.urljoin(url), self.parse_project)

        for nextpage in response.xpath("//a[name(..)='span'][../@class='next']/@href").extract():
            yield response.follow(nextpage,self.parse)

    def parse_project(self,response):
        for project_name in response.xpath("//h1[name(..)='div'][../@class='Project-visual__title']/a/text()").extract():
            yield {'project_name' : project_name}
