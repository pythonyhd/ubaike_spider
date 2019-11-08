# -*- coding: utf-8 -*-
# @Time    : 2019/9/25 15:07
# @Author  : Yasaka.Yu
# @File    : elasticsearch_common.py
import elasticsearch
from elasticsearch import helpers
from elasticsearch.helpers import bulk


class ESClient(object):

    def __init__(self, host="114.115.129.113", port=9999, index_name=None, index_type=None):
        self.index_name = index_name
        self.index_type = index_type
        # self.es = elasticsearch.Elasticsearch([{'host': '127.0.0.1', 'port': '9200'}],timeout=3000)
        self.es = elasticsearch.Elasticsearch([{'host': host, 'port': port}], timeout=3600)

    def insert_data(self, item, _id):
        result = self.es.create(index=self.index_name, doc_type=self.index_type, id=_id, body=item)
        return result

    def update_data(self, item, _id):
        item = {'doc': item}
        result = self.es.update(index=self.index_name, doc_type=self.index_type, id=_id, body=item)
        return result

    def update_by_query(self, query):
        result = self.es.update_by_query(index=self.index_name, doc_type=self.index_type, body=query)
        return result

    # 单条查询
    def search_by_query(self, query):
        result = self.es.search(index=self.index_name,  body=query)
        return result

    def search_all(self, item):
        result = self.es.search(index=self.index_name, body=item)
        return result

    def get_data_by_id(self, _id):
        result = self.es.get(index=self.index_name, doc_type=self.index_type, id=_id, ignore=[404])
        return result

    def add_data(self, row_obj):
        """
        单条插入ES
        """
        _id = row_obj.get("_id", 1)
        row_obj.pop("_id")
        self.es.index(index=self.index_name, doc_type=self.index_type, body=row_obj, id=_id)

    def add_data_bulk(self, row_obj_list):
        """
        批量插入ES
        """
        load_data = []
        i = 1
        bulk_num = 20000  # 2000条为一批
        for row_obj in row_obj_list:
            action = {
                "_index": self.index_name,
                "_type": self.index_type,
                "_id": row_obj.get('_id', 'None'),
                "_source": {
                    'oname': row_obj.get('oname', None),
                    'uccode': row_obj.get('uccode', None),
                    'cf_sy': row_obj.get('cf_sy', None),
                    'cf_jg': row_obj.get('cf_jg', None),
                    'cf_cflb': row_obj.get('cf_cflb', None),
                    'cf_jdrq': row_obj.get('cf_jdrq', None),
                    'cf_wsh': row_obj.get('cf_wsh', None),
                    'cf_xzjg': row_obj.get('cf_xzjg', None),
                    'sj_type': '67',
                    "site_id": 20906,
                    "xxly": '中华人民共和国-失信联合惩戒名单',
                    "cf_type": '失信联合惩戒',
                }
            }
            load_data.append(action)
            i += 1
            # 批量处理
            if len(load_data) == bulk_num:
                print('批量插入')
                success, failed = bulk(self.es, load_data, index=self.index_name, raise_on_error=True)
                del load_data[0:len(load_data)]
                print(success, failed)
                # print("一次共插入:%s条数据" % (len(load_data)))

        if len(load_data) > 0:
            success, failed = bulk(self.es, load_data, index=self.index_name, raise_on_error=True)
            print("插入成功")
            del load_data[0:len(load_data)]
            print(success, failed)

    def get_es_id(self):
        """
        获取es唯一id
        :return:
        """
        query = {
            "query": {"match": {
                "oname": "深圳"
            }},
            "size": 20
        }
        result = self.search_by_query(query)
        hits_data = result.get("hits").get("hits")
        for items in hits_data:
            _id = items.get("_id")
            yield _id

    def scroll_search(self, query_body, scroll='3m'):
        """
        游标遍历es库，返回的是生成器类型
        :param query_body: 查询数据语句
        :return: 查询的生成器
        """
        es_result = helpers.scan(
            client=self.es,
            query=query_body,
            scroll=scroll,
            index=self.index_name,
        )
        return es_result

    def get_query_body(self):
        # 检索选项
        query_body = {
            "query": {
                "match": {"oname": "深圳"}
            }
        }
        return query_body


if __name__ == '__main__':
    es_client = ESClient(index_name="company_index_db", index_type="company")
    # datas = es_client.get_es_id()
    result = es_client.get_data_by_id("80ab0f5fc0201359e3a5a2ab340f7a2d")
    print(result)
    print(type(result.get("_source")))