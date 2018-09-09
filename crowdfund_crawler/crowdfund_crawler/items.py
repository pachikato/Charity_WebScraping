import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst
import re

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


class DonationProject(scrapy.Item):
    # 時系列で変化しない、固定の取得項目
    project_name = scrapy.Field()
    system = scrapy.Field()
    end_date = scrapy.Field() # プロジェクトの期日、期日から二日以上経過したプロジェクトは取得しない
    category = scrapy.Field()
    donation_idx = scrapy.Field()
    donation_unit_price = scrapy.Field()
    return_list = scrapy.Field()
    source = scrapy.Field() # 取得元、今回であればReadyfor かCampfireの２択
    created_at = scrapy.Field()


class DonationLog(scrapy.Item):
    # 時系列の取得項目
    access_date = scrapy.Field()
    project_name = scrapy.Field()
    donation_idx = scrapy.Field()
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
        if type(s) is str:
            return s.strip()
        else:
            return s

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
    ## DonationProjectクラスとDonationLogで定義したアイテム名から、'アイテム名'_in　の命名規則で記述している
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
    patron_in = MapCompose(
        _ProcRemoveBlank
        , _ProcRemoveEmBlank
        , _ProcConvertKanji
        , _ProcRemoveComma
        , _ProcCastNumeric
    )
