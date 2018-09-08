import scrapy
from crowdfund_crawler.items import DonationProject, DonationProjectLoader


class CampfireSpider(scrapy.Spider):
    name = 'campfire_spider'
    allowed_domains = ['camp-fire.jp']
    # エンドポイント（クローリングを開始するURLを記載する）
    start_urls = [
        'http://camp-fire.jp/projects/category/social-good/popular'
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
    }

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

        # プロジェクトごとの項目を抜き出す
        item_loader = DonationProjectLoader(item=DonationProject(), response=response)

        item_loader.add_xpath('project_name', "//div[@class='header_top']/h2[@class='header_top__title']/text()")

        yield item_loader.load_item()

        self.logger.info('Complete project page parsing.')
