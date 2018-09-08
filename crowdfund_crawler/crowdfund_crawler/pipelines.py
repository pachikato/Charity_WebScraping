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
        if not item['project_name']:
            # project_nameフィールドが取得できていない場合は破棄する。
            raise DropItem('Missing project_name')

        return item
