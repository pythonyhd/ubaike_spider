# -*- coding: utf-8 -*-
import pymysql
from DBUtils.PooledDB import PooledDB


class MysqlClient(object):

    def __init__(self, host="127.0.0.1", port=3306, user="root", password="allen", db="works", conn_num=3):

        self.mysql_pool = PooledDB(pymysql, conn_num, host=host, port=port, user=user, passwd=password, db=db)

    def get_conn(self):
        """
        获取mysql连接
        """
        return self.mysql_pool.connection()

    def insert(self, table, item, start=0, end=-1):
        """
        插入item,到mysql制定的表中, 如果插入失败
        :param item: dict类型的数据，并且item中key的名称和mysql一致
        """
        fields = ", ".join(list(item.keys()))
        sub_char = ", ".join(["%s"]*len(item))
        values = tuple(list(item.values()))

        sql = "insert into %s(%s) values (%s)" % (table, fields, sub_char)

        conn = self.mysql_pool.connection()

        cursor = conn.cursor()

        try:
            result = cursor.execute(sql, values)
            conn.commit()
            return 1
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def insert_many(self, table, items):
        """
        插入多条数据,利用executemany方法
        :param table: 表名
        :param items: 插入的数据，可迭代对象
        """
        item = items[0]

        fields = ", ".join(list(item.keys()))
        sub_char = ", ".join(["%s"]*len(item))
        value_list = []
        for item in items:
            value = tuple(list(item.values()))
            value_list.append(value)

        sql = "insert into %s(%s) values (%s)" % (table, fields, sub_char)

        # 获取mysql连接和事务
        conn = self.mysql_pool.connection()
        cursor = conn.cursor()

        try:
            result = cursor.executemany(sql, value_list)
            conn.commit()
            return 1
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def update_one(self, table, update_item, condition):
        """
        更新表中某个字段
        :param table: mysql 表名
        :param items: dict, 要更新的字段,
        :param condition: dict, 筛选要更新的字段
        :return: None
        """
        fields = ", ".join(['{}="{}"'.format(key, value) for key, value in update_item.items()])
        filter_condition = " and ".join(['{}="{}"'.format(key, value) for key, value in condition.items()])

        sql = "update %s set %s where %s" % (table, fields, filter_condition)

        conn = self.mysql_pool.connection()
        cursor = conn.cursor()

        try:
            result = cursor.execute(sql)
            conn.commit()
            return 1
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def update_by_sql(self, sql):
        """
        通过sql语句更新
        """
        conn = self.mysql_pool.connection()
        cursor = conn.cursor()

        try:
            result = cursor.execute(sql)
            conn.commit()
            return 1
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def query(self, sql):
        """
        查询
        :param table: 表名
        :param sql: 查询的sql语句
        :return:
        """

        conn = self.mysql_pool.connection()
        cursor = conn.cursor()

        try:
            nums = cursor.execute(sql)
            conn.commit()
            result = cursor.fetchall()
            return result
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()

    def execute(self, sql):
        """
        执行sql语句,不返回数据
        """
        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            result = cursor.execute(sql)
            conn.commit()
            return 1
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()


if __name__ == '__main__':
    client = MysqlClient()
    client.update_one("work", {"a": 1, "b": 2}, {"id": 2})
