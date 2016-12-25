# coding:utf-8
# author: luyf
# create date: 2016.12.14
import urllib2

import time
from bs4 import BeautifulSoup
from pysqlite2 import dbapi2 as sqlite
import re
from gevent import monkey; monkey.patch_all()
import gevent


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
        self.con.execute('create table urllist(url)')
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
            print 'Insert to db: %s ' % value
            cur = self.con.execute(
                "insert into %s (%s) values ('%s')" % (table, file_id, value)
            )
            return cur.lastrowid
        else:
            print 'Exist: %s ' % value
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
        try:
            request = urllib2.Request(url, headers=headers)
            response = urllib2.urlopen(request, timeout=5)  # 超时设置
            result = response.read()
            time.sleep(3)
            return result
        except:
            print '----------------error------------------'
            return ''

    def get_stations_url(self, root_url):
        """
        抓取途牛首页 全国各地分站点url, 形如：上海站：http://sh.tuniu.com
        :return:分站点url字典，形如：{上海:http://sh.tuniu.com}
        """
        stations_url_dict = {}  # 存储超链接字典，出发站名：出发站独立url
        soup = BeautifulSoup(self.get_html(root_url), 'lxml')
        tag_div_list = soup.find_all('div', attrs={"class": "tagBox"})  # 搜索特定div标签内的超链接
        if tag_div_list is None:
            return stations_url_dict
        soup = BeautifulSoup(str(tag_div_list[0]), 'lxml')
        tag_a_list = soup.find_all('a', attrs={'href': True})
        tag_a_set = set(filter(lambda x: x['href'].startswith('http://') and x['href'].endswith('.com'), tag_a_list))

        for item in tag_a_set:
            stations_url_dict[item.get_text(strip=True)] = item['href']

        return stations_url_dict

    def get_catalog_url(self, stations_url):
        """
        抓取1个分站点首页的 旅游项目目录，如：上海周边游中的各个景点 如：普陀山：http://www.tuniu.com/guide/v-pts-8501/?pcat=5882
        :param stations_url:出发分站点url，如：http://sh.tuniu.com
        :return: 目的地的 名称 和 url 的字典，如：{普陀山:http://www.tuniu.com/guide/v-pts-8501/?pcat=5882}
        """
        soup = BeautifulSoup(self.get_html(stations_url), 'html5lib')
        tag_div_list = soup.find_all('div', attrs={"class": "catalog_third"})
        destinations_dict = {}  # 存储 目的地名称 和 url 的字典 如：普陀山：http://www.tuniu.com/guide/v-pts-8501/?pcat=5882
        if tag_div_list is None:
            return destinations_dict
        soup = BeautifulSoup(str(tag_div_list[0]), 'html5lib')
        tag_a_list = soup.find_all('a', attrs={'href': True})
        destinations_url_set = set(filter(lambda x: x['href'].startswith('http://') and x.get_text(strip=True) != '', tag_a_list))
        for item in destinations_url_set:
            destinations_dict[item.get_text(strip=True)] = item['href']

        return destinations_dict

    def get_details_url(self, departure_name, destination_name, route_list_url):
        """
        抓取列表页详细url,并存入数据库,如：http://www.tuniu.com/tour/210052165
        :param departure_name: 出发地
        :param destination_name: 目的地
        :param route_list_url: 路线列表页url,如http://www.tuniu.com/guide/v-pts-8501/?pcat=5882
        :return:
        """
        route_id_regex = re.compile(r'http://www\.tuniu\.com/(?:tour|tours)/(?P<route_id>\d{9})')
        route_id_ret = route_id_regex.findall(self.get_html(route_list_url))
        route_id_set = set(item for item in route_id_ret)

        url_id_set = set()
        for item in route_id_set:
            url = 'http://www.tuniu.com/tour/' + item
            url_id = self.get_entry_id('urllist', 'url', url)
            self.con.execute("insert into routeinfo(urlid, departure, destination) values(%d, '%s', '%s')" % (url_id, departure_name, destination_name))
            url_id_set.add(url_id)
        self.db_commit()

if __name__ == '__main__':
    clawled_departures = set([u'海城市', u'南充', u'梅河口市', u'焦作', u'古交市', u'麻城市', u'佛山', u'惠安县', u'虎林市', u'丹阳市',
                              u'鹿邑县', u'冷水江市', u'恩施', u'孟州市', u'连州市', u'肥乡县', u'鹤岗',u'合肥', u'江阴', u'安阳',
                              u'东兴市', u'栾城县', u'鸡西', u'阿拉善左旗', u'黑河'])  # 记录已抓取的出发地，中断后，词列表中的出发地不再抓取
    crawler_obj = TravelCrawler('travel_info.db')
    # crawler_obj.create_index_tables()  # 首次运行程序，创建数据库表
    test_url = 'http://www.tuniu.com/'
    test_departure_url_dict = crawler_obj.get_stations_url(test_url)
    print 'test_departure_url_dict: %d' % len(test_departure_url_dict)
    print test_departure_url_dict
    left_departure_num = len(test_departure_url_dict)

    # test_dep_des_url_dict = dict()  # {出发地:{目的地:目的地路线列表url}}
    for departure_name, departure_url in test_departure_url_dict.items():
        left_departure_num -= 1
        if departure_name in clawled_departures:
            continue
        print 'Left %d departure, Departure %s: %s ' % (left_departure_num, departure_name, departure_url)
        test_des_url_dict = crawler_obj.get_catalog_url(departure_url)
        print 'test_des_url_dict: %d' % len(test_des_url_dict)
        print test_des_url_dict

        gevent_list = []
        left_destinations_num = len(test_des_url_dict)
        for destination_name, destination_url in test_des_url_dict.items():
            left_destinations_num -= 1
            print 'Departure %s, Left %d destinations, Destination %s: %s' % (departure_name, left_destinations_num, destination_name, destination_url)
            gevent_list.append(gevent.spawn(crawler_obj.get_details_url, departure_name, destination_name, destination_url))
            gevent.joinall(gevent_list)
        # test_dep_des_url_dict[departure_name] = test_des_url_dict

