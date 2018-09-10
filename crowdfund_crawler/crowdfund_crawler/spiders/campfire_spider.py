import scrapy
from crowdfund_crawler.items import DonationProject, DonationLog, DonationLoader
from datetime import datetime


class CampfireSpider(scrapy.Spider):
    name = 'campfire_spider'
    allowed_domains = ['camp-fire.jp']
    start_urls = [
        'http://camp-fire.jp/projects/category/social-good/popular'
    ]
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
    }
    current_date = datetime.now().strftime("%Y-%m-%d")

    def parse(self, response):
        self.logger.info('start parsing.')

        # プロジェクトごとのURLを取得
        for url in response.xpath("//div[@class='box-in']/div[@class='box-thumbnail']/a[contains(@href, '/projects/view/')]/@href"):
            yield scrapy.Request(response.urljoin(url.extract()), self.parse_projects)

        # このページのパースが終わったら次ページで移って同じ処理を行う
        for next_page in response.xpath("//div[@class='pagination']//a[contains(text(), '次のページ')]/@href"):
            yield response.follow(next_page, self.parse)

        self.logger.info('End parsing.')

    def parse_projects(self, response):
        self.logger.info('Start project page parsing.')

        # プロジェクト名
        project_name = response.xpath("//div[@class='header_top']/h2[@class='header_top__title']/text()").extract_first()

        # 募集方式
        system = response.xpath("//div[@class='project_status']/div[@class='status']/p/strong/text()|//section[@class='all-in']/text()").re_first("All-In|All-or-Nothing")

        # 募集期日
        end_date = response.xpath("//div[@class='project_status']/div[@class='status']/p/strong/text()|//section[@class='all-in']/strong/text()").re_first(r'\d{4}/\d{1,2}/\d{1,2}').replace('/', '-')

        # カテゴリ
        category = response.xpath("//section[@class='title']//a[contains(@href,'/projects/category/')]/text()|//div[@class='header_top']//a[contains(@href,'/projects/category/')]/text()").extract_first()

        # 寄付金額ごとの項目を取り出す
        donation_idx = 1
        for return_section in response.xpath("//aside[@id='return__section']"):
            # 寄付金額
            donation_unit_price = return_section.xpath(".//div[@class='return__price']/span/text()").extract_first()
            # リターン
            return_list = return_section.xpath(".//p[@class='return__list readmore']/text()").extract()
            # パトロン
            patron = return_section.xpath(".//div[@class='return__info']/text()").re_first(r'(?<=パトロン：)(.*)(?=人)')
            # ストック　
            stock = '-1'

            # 募集期間で変化しない項目をproject_loaderに追加
            project_loader = DonationLoader(item=DonationProject(), response=response)
            project_loader.add_value('project_name', project_name)
            project_loader.add_value('system', system)
            project_loader.add_value('end_date', end_date)
            project_loader.add_value('category', category)
            project_loader.add_value('source', 'campfire')
            project_loader.add_value('donation_idx', donation_idx)
            project_loader.add_value('donation_unit_price', donation_unit_price)
            project_loader.add_value('return_list', return_list)
            project_loader.add_value('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # 時系列で変化する項目をlog_loaderに追加
            log_loader = DonationLoader(item=DonationLog(), response=response)
            log_loader.add_value('access_date', self.current_date)
            log_loader.add_value('project_name', project_name)
            log_loader.add_value('donation_idx', donation_idx)
            log_loader.add_value('donation_unit_price', donation_unit_price)
            log_loader.add_value('patron', patron)
            log_loader.add_value('stock', stock)

            # 寄付内容のidを更新する
            donation_idx += 1

            yield {'donation_project': project_loader.load_item(), 'donation_log': log_loader.load_item()}

        self.logger.info('Complete project page parsing.')
