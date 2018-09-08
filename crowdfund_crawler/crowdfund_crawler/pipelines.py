from scrapy.exceptions import DropItem


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class CrowdfundCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class ValidationPipeline(object):
    """
    Itemを検証するPipeline
    """

    def process_item(self, item, spider):
        # ここに書いた項目が取得できなかった場合はエラーにする
        if not item['project_name']:
            raise DropItem('Missing project_name')
        if not item['donation_unit_price']:
            raise DropItem('Missing donation_unit_price')
        return item
