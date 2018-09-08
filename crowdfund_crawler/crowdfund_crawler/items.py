import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst
import re

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


class DonationProject(scrapy.Item):
    project_name = scrapy.Field()
    end_date = scrapy.Field()
    donation_unit_price = scrapy.Field()
    return_list = scrapy.Field()


class DonationLog(scrapy.Item):
    access_date = scrapy.Field()
    project_name = scrapy.Field()
    donation_unit_price = scrapy.Field()
    patron = scrapy.Field()


class DonationLoader(ItemLoader):
    default_input_processor = Identity()
    default_output_processor = Identity()

    # 各プロセッサの組み合わせ要素となるサブプロセッサ

    # 全角・半角スペースを全て削除する関数
    def _ProcRemoveBlank(s):
        pattern = re.compile(r'\s+')
        return re.sub(pattern, '', s)

    # 文字列の両端にある文字列だけ削除
    def _ProcRemoveEndsBlank(s):
        return s.strip()

    # 全角スペースを全て削除
    def _ProcRemoveEmBlank(s):
        return s.replace('　', '')

    # カンマ除去
    def _ProcRemoveComma(s):
        return s.replace(',', '')

    # 先頭プラス除去
    def _ProcRemoveHeadPlus(s):
        return s.lstrip('+')

    # 漢数字変換
    def _ProcConvertKanji(s):
        return s.replace('百', '00').\
            replace('千', '000').replace('万', '0000').replace('円', '')

    # 数値型化
    def _ProcCastNumeric(s):
        return None if s == '' else\
            int(s) if s.find('.') < 0 else\
            float(s)

    # 各Fieldに対するプロセッサ
    default_input_processor = MapCompose(_ProcRemoveEndsBlank)
    default_output_processor = TakeFirst()

    # 各フィールドに個別のプロセッサ
    project_name_in = MapCompose(
        _ProcRemoveEndsBlank
        , _ProcRemoveEmBlank
    )
    donation_unit_price_in = MapCompose(
        _ProcRemoveEndsBlank
        , _ProcRemoveEmBlank
        , _ProcRemoveHeadPlus
        , _ProcConvertKanji
        , _ProcRemoveComma
        , _ProcCastNumeric
    )

