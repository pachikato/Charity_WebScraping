### how to test run
#1. type "activate scrapyenv" on cmd
#2. change directory by typing "E:" and "cd hoge"
#3. run by command "scrapy runspider readyfor_spider.py -o hoge.json"
#4. see the output hoge.json by command "type test.json"
#5. If text garbling, command "chcp 65001" to change to utf-8.
#USEFUL!! command "scrapy shell (web address)" can check the running immidiately. we can end by command "exit()"
####################

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
        project_name = response.xpath("//h1[name(..)='div'][../@class='Project-visual__title']/a/text()").extract_first()
        system = response.xpath("//div[contains(@class,'project-attributes-badge')]/div[2]/text()").extract_first()
        end_date = response.xpath("//div[contains(@class,'Project-visual__body')]/p/text()").re(r'\d{1,2}月\d{1,2}日')[0]
        for i in range(1, len(response.xpath("//section[@class='Project-return Side-area-1 u-mb_20']").extract())):
            menulist = "//section[@class='Project-return Side-area-1 u-mb_20'][%s]" % i
            donation = response.xpath(menulist + "/descendant::span[@class='Project-return__price']/text()").extract_first()
            return_list = response.xpath(menulist + "/descendant::p[@class='Project-return__description u-mb_30']/text()").extract()
            yield {
            'project_name' : project_name, 'system' : system, 'end_date' : end_date, 'donation_unit_price' : donation, 'return_list' : return_list,
            }
