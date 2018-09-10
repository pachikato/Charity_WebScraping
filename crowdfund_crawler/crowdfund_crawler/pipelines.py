from scrapy.exceptions import DropItem
import psycopg2


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
        # ここに書いた項目が取得できなかった場合は破棄する
        if not item['donation_project']['project_name']:
            raise DropItem('Missing project_name')
        if not item['donation_log']['project_name']:
            raise DropItem('Missing project_name')

        # system とend_date の取得できないプロジェクトはスクレイピイング対象から外す
        if not item['donation_project']['system']:
            raise DropItem('Missing system')
        if not item['donation_project']['end_date']:
            raise DropItem('Missing end_date')

        return item


class PostgreSQLPipeline(object):
    """
    Item をPostgreSQLに保存するPipeline
    """

    def open_spider(self, spider):
        """
        Spiderの開始時にPostgreSQLサーバに接続する
        donation_projectテーブル、donation_logテーブルがない場合は作成する
        """

        settings = spider.settings
        params = {
            'host': settings.get('POSTGRESQL_HOST', 'localhost')
            , 'dbname': settings.get('POSTGRESQL_DATABASE', 'crowdfund')
            , 'user': settings.get('POSTGRESQL_USER', 'postgres')
            , 'password': settings.get('POSTGRESQL_PASSWORD', '')
            , 'port': settings.get('POSTGRESQL_PORT', 5432)
        }
        self.conn = psycopg2.connect(**params)
        self.cur = self.conn.cursor()

        # donation_project テーブル
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS donation_project (
                project_name VARCHAR(1024),
                system VARCHAR(50),
                end_date DATE,
                category VARCHAR(50),
                donation_idx INTEGER,
                donation_unit_price BIGINT,
                return_list TEXT,
                source VARCHAR(50),
                created_at TIMESTAMP,
                UNIQUE (project_name, donation_idx, source)
            )
        ''')
        self.conn.commit()

        # donation_log テーブル
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS donation_log (
                access_date DATE,
                project_name VARCHAR(1024),
                donation_idx INTEGER,
                donation_unit_price BIGINT,
                patron BIGINT,
                stock BIGINT,
                UNIQUE (access_date, project_name, donation_idx)
            )
        ''')
        self.conn.commit()

    def close_spider(self, spider):
        """
        Spiderの終了時にPostgreSQLサーバへの接続を切断する
        """

        self.conn.close()

    def process_item(self, item, spider):
        """
        Itemをdonation_projectテーブル、donation_logテーブルに挿入する
        """

        # donation_project テーブル
        self.cur.execute(
            '''
            INSERT INTO donation_project
                (
                    project_name
                    , system
                    , end_date
                    , category
                    , donation_idx
                    , donation_unit_price
                    , return_list
                    , source
                    , created_at
                )
                VALUES (
                    %(project_name)s
                    , %(system)s
                    , %(end_date)s
                    , %(category)s
                    , %(donation_idx)s
                    , %(donation_unit_price)s
                    , %(return_list)s
                    , %(source)s
                    , %(created_at)s
                )
                ON CONFLICT ON CONSTRAINT donation_project_project_name_donation_idx_source_key
                DO NOTHING
            '''
            , dict(item['donation_project'])
        )
        self.conn.commit()
        # donation_log テーブル
        self.cur.execute(
            '''
            INSERT INTO donation_log
                (
                    access_date
                    , project_name
                    , donation_idx
                    , donation_unit_price
                    , patron
                    , stock
                )
                VALUES (
                    %(access_date)s
                    , %(project_name)s
                    , %(donation_idx)s
                    , %(donation_unit_price)s
                    , %(patron)s
                    , %(stock)s
                )
                ON CONFLICT ON CONSTRAINT donation_log_access_date_project_name_donation_idx_key
                DO UPDATE SET patron=%(patron)s, stock=%(stock)s
            '''
            , dict(item['donation_log'])
        )
        self.conn.commit()
        return item
