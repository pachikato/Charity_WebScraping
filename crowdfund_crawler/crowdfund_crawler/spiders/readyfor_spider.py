### how to test run
#1. type "activate scrapyenv" on cmd
#2. change directory by typing "E:" and "cd hoge"
#3. run by command "scrapy runspider readyfor_spider.py -o hoge.json"
#4. see the output hoge.json by command "type test.json"
#5. If text garbling, command "chcp 65001" to change to utf-8.
#USEFUL!! command "scrapy shell (web address)" can check the running immidiately. we can end by command "exit()"
####################

### how to run by hand
#1. command "activate scrapyenv" on cmd
#2. change directory by typing "E:" and "cd hoge"
#3. run by command "scrapy crawl readyfor_spider -o readyfor.jl"
#4. Open by SQLWorkbenck.exe
###################

import scrapy
import re
from crowdfund_crawler.items import DonationProject, DonationLog, DonationLoader
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ReadyforSpider(scrapy.Spider):
    name = "readyfor_spider"
    allowed_domains = ['readyfor.jp']
    start_urls = ['https://readyfor.jp/tags/charity']
    custom_settings = {"DOWNLOAD_DELAY":1}
    current_date = datetime.now().strftime("%Y-%m-%d")

    def parse(self,response):
        self.logger.info("start parsing.")

        for url in response.xpath("//a[name(..)='article']/@href").extract():
            yield scrapy.Request(response.urljoin(url), self.parse_project)

        for nextpage in response.xpath("//a[name(..)='span'][../@class='next']/@href").extract():
            yield response.follow(nextpage,self.parse)

        self.logger.info("finish parsing.")

    def parse_project(self,response):
        self.logger.info('Start project page parsing.')

        #Project name
        project_name = response.xpath("//h1[name(..)='div'][../@class='Project-visual__title']/a/text()").extract_first()

        #Donation model
        system = response.xpath("//div[contains(@class,'project-attributes-badge')]/div[2]/text()").extract_first()

        #end_date
        end_date = response.xpath("//div[contains(@class,'Project-visual__body')]/p/text()").re_first(r'\d{1,2}月\d{1,2}日')
        if end_date == None:
            end_date = response.xpath("//div[contains(@class,'Project-visual__alert is-miss u-mt_15 u-mb_20')]/span/text()").re_first(r'\d{4}年\d{1,2}月\d{1,2}')
            if end_date == None:
                end_date = response.xpath("//div[contains(@class,'Project-visual__alert is-complete u-mt_15 u-mb_20')]/span[2]/text()").re_first(r'\d{4}年\d{1,2}月\d{1,2}')
            end_date = re.sub(r'\D','-',end_date)
            end_date = datetime.strptime(end_date,'%Y-%m-%d').strftime('%Y-%m-%d')
        else:
            end_date = end_date.replace('月','-').replace('日','')
            end_date = datetime.now().strftime('%Y-') + end_date
            end_date = datetime.strptime(end_date,'%Y-%m-%d')
            if datetime.now() < end_date:
                end_date = end_date.strftime('%Y-%m-%d')
            else:
                end_date = end_date + relativedelta(years=1)
                end_date = end_date.strftime('%Y-%m-%d')

        ###category must be set
        category = "hoge"

        ###Donation and Return variables
        donation_idx = 1
        for return_section in response.xpath("//a[@class='is-no-shadow u-fit-w u-mt_20 Side-area-1-txt']"):
            #Donation
            donation_unit_price = return_section.xpath(".//descendant::span[@class='Project-return__price']/text()").extract_first()
            #Return
            return_list = return_section.xpath(".//descendant::p[@class='Project-return__description u-mb_30']/text()").extract()
            #patron
            patron = return_section.xpath(".//descendant::span[@class='u-valign_m']/text()").re_first(r'\d+')
            #stock
            stock = return_section.xpath(".//descendant::span[@class='u-valign_m']/span/text()").extract_first()
            if stock == '在庫制限無し':
                stock = '-1'
            else:
                stock = re.search(r'\d+',stock).group()
            #Database for time-invariant
            project_loader = DonationLoader(item=DonationProject(), response=response)
            project_loader.add_value('project_name', project_name)
            project_loader.add_value('system', system)
            project_loader.add_value('end_date', end_date)
            project_loader.add_value('category', category)
            project_loader.add_value('source', 'ready for')
            project_loader.add_value('donation_idx', donation_idx)
            project_loader.add_value('donation_unit_price', donation_unit_price)
            project_loader.add_value('return_list', return_list)
            project_loader.add_value('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            #Database for time-variant variables
            log_loader = DonationLoader(item=DonationLog(), response=response)
            log_loader.add_value('access_date', self.current_date)
            log_loader.add_value('project_name', project_name)
            log_loader.add_value('donation_idx', donation_idx)
            log_loader.add_value('donation_unit_price', donation_unit_price)
            log_loader.add_value('patron', patron)
            log_loader.add_value('stock', stock)
            #Donation index + 1
            donation_idx += 1
            yield {'donation_project': project_loader.load_item(), 'donation_log': log_loader.load_item()}

        self.logger.info('Complete project page parsing.')
