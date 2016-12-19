# coding:utf-8
# author: luyf
# create date: 2016.12.14
import urllib2
from bs4 import BeautifulSoup
from pysqlite2 import dbapi2 as sqlite
import re


class TravelCrawler:
    def __init__(self, db_name):
        self.con = sqlite.connect(db_name)

    def __del__(self):
        self.con.close()

    def db_commit(self):
        self.con.commit()

    def create_index_tables(self):
        """
        为数据库的所有表建立schema，并建立一些只在加快搜索速度的索引
        :return:
        """
        self.con.execute('create table urllist(url, routeid)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid, wordid, location)')
        self.con.execute('create table routeinfo(urlid, departure, destination, routename)')
        self.con.execute('create table evaluation(urlid, score, price, comment, picture)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index departureidx on routeinfo(departure)')
        self.con.execute('create index destinationidx on routeinfo(destination)')

    def get_entry_id(self, table, file_id, value, create_new=True):
        """
        返回条目的id，如果该条目不存在，程序会在数据库中新建一条记录
        :param table: 表名
        :param file_id: 字段名
        :param value: 值
        :param create_new: 是否新建记录
        :return: 条目的id
        """
        cur = self.con.execute(
            "select rowid from %s where %s='%s'" % (table, file_id, value)
        )
        res = cur.fetchone()
        if res is None:  # 数据库不存在该条记录，新增
            cur = self.con.execute(
                "insert into %s (%s) values ('%s')" % (table, file_id, value)
            )
            return cur.lastrowid
        else:
            return res[0]

    def get_html(self, url):
        """
        发送请求，获取url页面html
        :param url:
        :return: 响应html
        """

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)  # 超时设置
        return response.read()

    def get_stations_url(self, root_url):
        """
        抓取途牛首页 全国各地分站点url, 形如：上海站：http://sh.tuniu.com
        :return:分站点url字典，形如：上海：http://sh.tuniu.com
        """
        soup = BeautifulSoup(self.get_html(root_url), 'lxml')
        tag_div_list = soup.find_all('div', attrs={"class": "tagBox"})  # 搜索特定div标签内的超链接
        soup = BeautifulSoup(str(tag_div_list[0]), 'lxml')
        stations_url_dict = {}  # 存储超链接字典，出发站名：出发站独立url
        tag_a_list = soup.find_all('a', attrs={'href': True})
        tag_a_set = set(filter(lambda x: x['href'].startswith('http://') and x['href'].endswith('.com'), tag_a_list))

        for item in tag_a_set:
            stations_url_dict[item.get_text(strip=True)] = item['href']

        return stations_url_dict

    def get_catalog_url(self, stations_url):
        """
        抓取各个分站点首页的 旅游项目目录，如：上海周边游中的各个景点 如：普陀山：http://www.tuniu.com/guide/v-pts-8501/?pcat=5882
        :param stations_url:出发分站点 名称和url 的字典
        :return:
        """
        dep_des_url_dict = {}  # {出发站:{目的地:目的地路线列表页url}}
        for (departure, departure_url) in stations_url.items():
            soup = BeautifulSoup(self.get_html(departure_url), 'html5lib')
            tag_div_list = soup.find_all('div', attrs={"class": "catalog_third"})

            soup = BeautifulSoup(str(tag_div_list[0]), 'html5lib')
            test_list = soup.find_all('a', attrs={'href': True})
            test_set = set(filter(lambda x: x['href'].startswith('http://') and x.get_text(strip=True) != '', test_list))

            destinations_dict = {}  # 存储 目的地名称 和 url 的字典 如：普陀山：http://www.tuniu.com/guide/v-pts-8501/?pcat=5882
            for item in test_set:
                destinations_dict[item.get_text(strip=True)] = item['href']

            dep_des_url_dict[departure] = destinations_dict
        return dep_des_url_dict

    def get_details_url(self, dep_des_url):
        """
        抓取列表页详细url,并存入数据库，如：http://www.tuniu.com/tour/210052165
        :param dep_des_url: 列表页url字典，{出发站:{目的地:目的地路线列表页url}}
        :return:
        """
        detail_url_set = set()
        for dep_item, des_url_dict_item in dep_des_url.items():
            for des_item, url_item in des_url_dict_item.items():
                    detail_url_regex = re.compile(r'http://www\.tuniu\.com/(?:tour|tours)/\d{9}')
                    detail_url_ret = detail_url_regex.findall(self.get_html(url_item))
                    tmp_detail_url_set = set(item for item in detail_url_ret)
                    detail_url_set.update(tmp_detail_url_set)

        url_id_set = set()
        for item in detail_url_set:
            print 'insert to db:%s ' % item
            url_id_set.update(self.get_entry_id('urllist', 'url', item))

crawler_obj = TravelCrawler('travel_info.db')
# crawler_obj.create_index_tables()  # 首次运行程序，创建数据库表
test_url = 'http://www.tuniu.com/'
test_stations_url_dict = crawler_obj.get_stations_url(test_url)
print 'test_stations_url_dict:\n'
print len(test_stations_url_dict)
print test_stations_url_dict
test_dep_des_url_dict = crawler_obj.get_catalog_url(test_stations_url_dict)
print 'test_dep_des_url_dict:\n'
print len(test_dep_des_url_dict)
print test_dep_des_url_dict

crawler_obj.get_details_url(test_dep_des_url_dict)
