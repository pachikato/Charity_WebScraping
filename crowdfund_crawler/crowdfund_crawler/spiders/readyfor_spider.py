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
        project_name = response.xpath("//h1[name(..)='div'][../@class='Project-visual__title']/a/text()").extract()
        for i in range(1, len(response.xpath("//section[@class='Project-return Side-area-1 u-mb_20']").extract())):
            menulist = "//section[@class='Project-return Side-area-1 u-mb_20'][%s]" % i
            donation = response.xpath(menulist + "/descendant::span[@class='Project-return__price']/text()").extract_first()
            return_list = response.xpath(menulist + "/descendant::p[@class='Project-return__description u-mb_30']/text()").extract()
            yield {'project_name' : project_name, 'donation' : donation, 'return_list' : return_list}
