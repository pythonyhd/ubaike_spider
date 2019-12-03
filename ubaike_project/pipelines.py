# -*- coding: utf-8 -*-
import time
from scrapy.exceptions import DropItem
from ubaike_project.work_utils.filter_fact import filter_factory
import pymongo
import redis
import pymysql
from twisted.enterprise import adbapi
import json
from ubaike_project.utils.mysql_common import MysqlClient
from ubaike_project.utils.elasticsearch_common import ESClient
from ubaike_project.work_utils.creat_mysql_data import Base, engine
from ubaike_project import settings
import logging
logger = logging.getLogger(__name__)


class UbaikeProjectPipeline(object):
    """
    添加必要字段
    """
    def process_item(self, item, spider):
        item['cj_sj'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        ws_pc_id = filter_factory(item)
        if ws_pc_id:
            item['ws_pc_id'] = ws_pc_id
        else:
            DropItem(item)
        return item


class MongoPipeline(object):
    """
    存储到mongodb
    """

    def __init__(self, mongo_uri, mongo_db):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATA_BASE')
        )

    # def open_spider(self, spider):  # 爬虫一旦开启，就会实现这个方法，连接到数据库
    #     self.collection = self.db[spider.name]  # 连表

    def process_item(self, item, spider):
        collection = self.db[item.get('sj_type')]
        if item:
            # self.collection.insert(dict(item))
            collection.update({'ws_pc_id': item['ws_pc_id']}, dict(item), True)
            # logger.info("数据插入成功:%s"%item)
            return item

    def close_spider(self, spider):
        self.client.close()


class MysqlPipeline(object):
    """
    存储到MySQL
    """
    def __init__(self, mysql_host, mysql_port, mysql_user, mysql_passwd, mysql_db, mysql_charset, redis_host, redis_port, redis_password, redis_db):
        self.mysql_client = MysqlClient(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            passwd=mysql_passwd,
            db=mysql_db,
            charset=mysql_charset,
        )

        self.redis_client = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=redis_db,
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host=crawler.settings.get('DB_HOST'),
            mysql_port=crawler.settings.get('DB_PORT'),
            mysql_user=crawler.settings.get('DB_USER'),
            mysql_passwd=crawler.settings.get('DB_PASSWORD'),
            mysql_db=crawler.settings.get('DB_NAME'),
            mysql_charset=crawler.settings.get('DB_CHARSET'),

            redis_host=crawler.settings.get('REDIS_HOST'),
            redis_port=crawler.settings.get('REDIS_PORT'),
            redis_password=crawler.settings.get('REDIS_PASSWORD'),
            redis_db=crawler.settings.get('REDIS_DB'),
        )

    def open_spider(self, spider):
        Base.metadata.create_all(engine)

    def process_item(self, item, spider):
        if item.get('sj_type') == 'base':
            # item.pop('sj_type')
            try:
                self.mysql_client.insert('hd_base_info', dict(item))
                logger.info('插入成功- {} - '.format(item.get('oname')))
            except Exception as e:
                if 'Duplicate' not in repr(e):
                    # item['sj_type'] = "base"  # 把被排重的字段暂时存下来，有可能是排重规则有问题
                    self.redis_client.sadd(spider.name + ":insert_err_items", json.dumps(dict(item), ensure_ascii=False))

        elif item.get('sj_type') == 'gdinfo':
            # item.pop('sj_type')
            try:
                self.mysql_client.insert('hd_gd_info', dict(item))
            except Exception as e:
                if 'Duplicate' not in repr(e):
                    # item['sj_type'] = "gdinfo"  # 把被排重的字段暂时存下来，有可能是排重规则有问题
                    self.redis_client.sadd(spider.name + ":insert_err_items", json.dumps(dict(item), ensure_ascii=False))

        elif item.get('sj_type') == 'main_people':
            # item.pop('sj_type')
            try:
                self.mysql_client.insert('hd_major_info', dict(item))
            except Exception as e:
                if 'Duplicate' not in repr(e):
                    # item['sj_type'] = "main_people"  # 把被排重的字段暂时存下来，有可能是排重规则有问题
                    self.redis_client.sadd(spider.name + ":insert_err_items", json.dumps(dict(item), ensure_ascii=False))

        elif item.get('sj_type') == 'change':
            # item.pop('sj_type')
            try:
                self.mysql_client.insert('hd_change_info', dict(item))
            except Exception as e:
                if 'Duplicate' not in repr(e):
                    # item['sj_type'] = "change"  # 把被排重的字段暂时存下来，有可能是排重规则有问题
                    self.redis_client.sadd(spider.name + ":insert_err_items", json.dumps(dict(item), ensure_ascii=False))

        elif item.get('sj_type') == 'jyyc':
            # item.pop('sj_type')
            try:
                self.mysql_client.insert('hd_jyyc_info', dict(item))
            except Exception as e:
                if 'Duplicate' not in repr(e):
                    # item['sj_type'] = "jyyc"  # 把被排重的字段暂时存下来，有可能是排重规则有问题
                    self.redis_client.sadd(spider.name + ":insert_err_items", json.dumps(dict(item), ensure_ascii=False))

        elif item.get('sj_type') == 'sxinfo':
            # item.pop('sj_type')
            try:
                self.mysql_client.insert('hd_sxbzxr_info', dict(item))
            except Exception as e:
                if 'Duplicate' not in repr(e):
                    # item['sj_type'] = "sxinfo"  # 把被排重的字段暂时存下来，有可能是排重规则有问题
                    self.redis_client.sadd(spider.name + ":insert_err_items", json.dumps(dict(item), ensure_ascii=False))


# todo 异步插入MySQL
class MysqlTwistedPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.redis_client = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
        )

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["DB_HOST"],
            db=settings["DB_NAME"],
            user=settings["DB_USER"],
            passwd=settings["DB_PASSWORD"],
            charset=settings["DB_CHARSET"],
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparms)  # 连接
        return cls(dbpool)

    def open_spider(self, spider):
        Base.metadata.create_all(engine)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)  # 调用twisted进行异步的插入操作
        logger.debug("成功插入MySQL,公司名称:%s" % item.get("oname"))
        query.addErrback(self.handle_error,item,spider)

    def do_insert(self, cursor, item):
        # sql = "insert into area(id, aname, lv, pid) values(%s,%s,%s,%s)"
        # params = (item["id"], item["aname"], item["lv"], item["pid"])
        # try:
        #     cursor.execute(sql, params)
        # except Exception as e:
        #     print(e.args)
        sj_type = item.get('sj_type')
        if sj_type == 'base':
            table = 'hd_base_info'
            try:
                self.insert_to_sql(table, cursor, dict(item))
                logger.info('插入成功:{}'.format(item.get('oname')))
            except Exception as e:
                logger.error('插入失败,errormsg:{}'.format(repr(e)))
                # self.redis_client.sadd("ubaike:insert_err_items", json.dumps(dict(item), ensure_ascii=False))

        elif sj_type == 'gdinfo':
            table = 'hd_gd_info'
            try:
                self.insert_to_sql(table, cursor, dict(item))
                logger.debug('插入成功:{}'.format(item.get('oname')))
            except Exception as e:
                logger.error('插入失败,errormsg:{}'.format(repr(e)))
                # self.redis_client.sadd("ubaike:insert_err_items", json.dumps(dict(item), ensure_ascii=False))

        elif sj_type == 'main_people':
            table = 'hd_major_info'
            try:
                self.insert_to_sql(table, cursor, dict(item))
                logger.debug('插入成功:{}'.format(item.get('oname')))
            except Exception as e:
                logger.error('插入失败,errormsg:{}'.format(repr(e)))
                # self.redis_client.sadd("ubaike:insert_err_items", json.dumps(dict(item), ensure_ascii=False))

        elif sj_type == 'change':
            table = 'hd_change_info'
            try:
                self.insert_to_sql(table, cursor, dict(item))
                logger.debug('插入成功:{}'.format(item.get('oname')))
            except Exception as e:
                logger.error('插入失败,errormsg:{}'.format(repr(e)))
                # self.redis_client.sadd("ubaike:insert_err_items", json.dumps(dict(item), ensure_ascii=False))

        elif sj_type == 'jyyc':
            table = 'hd_jyyc_info'
            try:
                self.insert_to_sql(table, cursor, dict(item))
                logger.info('插入成功:{}'.format(item.get('oname')))
            except Exception as e:
                logger.error('插入失败,errormsg:{}'.format(repr(e)))
                # self.redis_client.sadd("ubaike:insert_err_items", json.dumps(dict(item), ensure_ascii=False))

        elif sj_type == 'sxinfo':
            table = 'hd_sxbzxr_info'
            try:
                self.insert_to_sql(table, cursor, dict(item))
                logger.info('插入成功:{}'.format(item.get('oname')))
            except Exception as e:
                print(e)
                # logger.error('插入失败,保存到redis,errormsg:{}'.format(repr(e)))

    def insert_to_sql(self, table, cursor, item):
        fields = ", ".join(list(item.keys()))
        sub_char = ", ".join(["%s"]*len(item))
        values = tuple(list(item.values()))
        sql = "insert into %s(%s) values (%s)" % (table, fields, sub_char)

        try:
            cursor.execute(sql, values)
        except Exception as e:
            print('插入失败- {} - '.format(e.args))
            self.redis_client.sadd("ubaike:insert_err_items", json.dumps(dict(item), ensure_ascii=False))

    def handle_error(self, failure, item, spider):
        logger.error("插入失败原因:%s,公司名称:%s"%(failure, item.get("oname")))


class UpdateDataToEs(object):

    def open_spider(self, spider):
        self.es_client = ESClient(index_name=settings.INDEX_NAME, index_type=settings.INDEX_TYPE)

    def process_item(self, item, spider):
        if item:
            _id = item.get("ws_pc_id")
            res = self.es_client.get_data_by_id(_id)
            if res.get("found") == True:
                logger.info("数据存在,更新数据")
                self.es_client.update_data(dict(item), _id)
            else:
                logger.info("数据不存在,插入数据")
                self.es_client.insert_data(dict(item), _id)

    def close_spider(self,spider):
        pass