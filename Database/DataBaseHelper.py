# coding: utf-8
# author: luyf
# create date: 2016.12.23

import sqlite3


class DataBaseHelper:

    def __init__(self, db_path):
        """
        建立数据库连接
        :param db_path:数据库路径
        """
        self.database = sqlite3.connect(db_path)
        self.cursor = self.database.cursor()
        self.create_table()

    def __del__(self):
        self.cursor.close()
        self.database.close()

    def create_table(self):
        """
        创建数据库表结构
        :return:
        """
        self.cursor.execute("create table if not exists subsite(subsiteurl varchar primary key, subsitename varchar)")
        self.cursor.execute("create index if not exists subsiteurlindex on subsite(subsiteurl)")

        self.cursor.execute("create table if not exists routeurl(url varchar primary key)")
        self.cursor.execute("create index if not exists urlindex on routeurl(url)")

        self.cursor.execute("create table if not exists routeinfo(urlid integer primary key,title varchar,satisfaction integer,summary varchar,text varchar)")
        self.cursor.execute("create index if not exists urlidindex on routeinfo(urlid)")

        self.cursor.execute("create table if not exists routedep(urlid integer, departure varchar,price integer, primary key(urlid, departure))")
        self.cursor.execute("create index if not exists departureindex on routedep(departure)")

        self.cursor.execute("create table if not exists routecom(urlid integer, outline varchar,detail varchar primary key)")
        self.cursor.execute("create index if not exists detailindex on routecom(detail)")

        self.cursor.execute("create table if not exists routeerrorurl(errorurl varchar primary key)")
        self.cursor.execute("create index if not exists errorurlindex on routeerrorurl(errorurl)")

        self.database.commit()

    def is_exist(self, table_name, file_id, value):
        """
        判断某条记录是否存在
        :param table_name:数据库表名
        :param file_id: 记录名
        :param value: 记录值
        :return: 若存在，返回第一条记录，否则返回None
        """
        command = "select rowid from %s where %s = '%s'" % (table_name, file_id, value)
        self.cursor.execute(command)
        result = self.cursor.fetchone()
        # return True if result is not None else False
        return result[0] if result is not None else None

    def insert_into_routeurl(self, url):
        """
        插入新url到urllist数据库
        :param url:
        :return:
        """
        if self.is_exist('routeurl', 'url', url) is not None:
            print 'Exist url: %s' % url
        else:
            command = "insert into routeurl(url) values('%s')" % url
            self.cursor.execute(command)
            self.database.commit()
            print 'Insert url: %s' % url

    def insert_into_subsite(self, subsite_url, subsite_name):
        """
        插入新的分站点记录
        :param subsite_url:
        :param subsite_name:
        :return:
        """
        if self.is_exist('subsite', 'subsiteurl', subsite_url) is not None:
            print 'Exist subsite: %s' % subsite_url
        else:
            command = "insert into subsite(subsiteurl, subsitename) values('%s','%s')" % (subsite_url, subsite_name)
            self.cursor.execute(command)
            self.database.commit()
            print 'Insert subsite: %s' % subsite_url

    def insert_into_routeinfo(self, urlid, title, satisfaction, summary, text):
        """
        插入路线详细信息到数据表routeinfo
        :param urlid:
        :param title:
        :param satisfaction:
        :param summary:
        :param text:
        :return:
        """
        if self.is_exist('routeinfo', 'urlid', urlid) is not None:  # 数据存在，更新数据
            print 'Exist routeinfo: %s' % urlid
            # command = "update routeinfo set title = '%s', satisfaction = %d, summary = '%s', text = '%s' where urlid=%d" \
            #           % (title, satisfaction, summary, text, urlid)
            # print 'Update routeinfo %d' % urlid
        else:
            command = "insert into routeinfo(urlid, title, satisfaction, summary, text) values(%d, '%s', %d, '%s', '%s')" % (urlid, title, satisfaction, summary, text)
            print 'Insert routeinfo %d' % urlid
            self.cursor.execute(command)
            self.database.commit()

    def insert_into_routecom(self, urlid, outline, detail):
        """
        插入路线评论信息到数据表routecom
        :param urlid:
        :param outline:
        :param detail:
        :return:
        """
        if self.is_exist('routecom', 'detail', detail) is not None:  # 数据存在，更新数据
            print 'Exist routecom: %s' % urlid
            # command = "update routecom set urlid = %d, outline = '%s' where detail= '%s'" \
            #           % (urlid, outline, detail)
            # print 'Update routecom %d' % urlid
        else:
            command = "insert into routecom(urlid, outline, detail) values(%d, '%s', '%s')" % (urlid, outline, detail)
            print 'Insert routecom %d' % urlid
            self.cursor.execute(command)
            self.database.commit()

    def insert_into_routedep(self, urlid, departure, price):
        """
        插入路线出发地及价格到数据表 routedep
        :param urlid:
        :param departure:
        :param price:
        :return:
        """
        exist_command = "select rowid from routedep where urlid=%d and departure='%s'" % (urlid, departure)
        self.cursor.execute(exist_command)
        if self.cursor.fetchone() is not None:  # 数据存在，更新数据
            print 'Exist routedep: %s' % urlid
            # command = "update routedep set price = %d where urlid=%d and departure='%s'" % (price, urlid, departure)
            # print 'Update routedep %d' % urlid
        else:
            command = "insert into routedep(urlid, departure, price) values(%d, '%s', %d)" % (urlid, departure, price)
            print 'Insert routedep %d' % urlid
            self.cursor.execute(command)
            self.database.commit()

    def insert_into_routeerrorurl(self, url):
        """
        插入请求出错的url到数据表errorurl
        :param url:
        :return:
        """
        if self.is_exist('routeerrorurl', 'errorurl', url) is None:  # 数据不存在插入
            command = "insert into routeerrorurl(errorurl) values('%s')" % url
            self.cursor.execute(command)
            self.database.commit()

    # def select_all(self, table_name):
    #     """
    #     获取数据表数据
    #     :param table_name:
    #     :return: 返回查询结果列表
    #     """
    #     command = 'select * from %s' % table_name
    #     self.cursor.execute(command)
    #     result_list = self.cursor.fetchall()
    #     return result_list

    def select_all_data(self, table_name, file_id):
        """
        获取数据表数据
        :param table_name:
        :param file_id: 'ALL'表示查询数据表的所有数据，否则表示查询某一列数据
        :return:
        """
        if file_id == 'ALL':
            command = 'select * from %s' % table_name
        else:
            command = 'select %s from %s' % (file_id, table_name)
        self.cursor.execute(command)
        result_list = self.cursor.fetchall()
        return result_list

    def select_one_data(self, file_name1, table_name, file_name2, value):
        command = "select %s from %s where %s = '%s'" % (file_name1, table_name, file_name2, value)
        self.cursor.execute(command)
        result_list = self.cursor.fetchall()
        return result_list

    def get_table_count(self, table_name):
        """
        获取表长度
        :param table_name:
        :return:
        """
        command = 'select count(*) from %s' % table_name
        self.cursor.execute(command)
        return self.cursor.fetchone()[0]

    # def insert_into_db(self, table_name, record_dict):
    #     """
    #     数据库插入新数据
    #     :param table_name: 数据库表名
    #     :param record_dict: 数据库表 记录名和记录值 字典，如 ：{subsite_name:subsite_url}
    #     :return:
    #     """
    #     record_name = ''
    #     record_values = ''
    #     if self.is_exist(table_name, record_dict.items()[0][0], record_dict.items()[0][1]):
    #         print 'Exist record: %s' % record_dict
    #     else:
    #         record_num = len(record_dict)
    #         for item in record_dict.items():
    #             record_name += item[0] + ','
    #             record_values += item[1] + ','
    #         record_name = record_name[:-1]  # 去除最后多余的','
    #         record_values = record_values[:-1]
    #         command = 'insert into %s(%s) values(%s)' % (table_name, record_name, record_values)
    #         self.cursor.execute(command)
    #         self.database.commit()
    #         print 'Insert: %s' % url

#
# if __name__ == '__main__':
#     obj = DataBaseHelper('TravelInfo.db')
#     obj.create_table()
