# coding:utf-8
# author: luyf
# create date: 2016.12.14
import urllib2
import time
from bs4 import BeautifulSoup
import re
from gevent import monkey; monkey.patch_all()
import gevent
import sys
sys.path.append("..")
from Database.DataBaseHelper import *

DB_PATH = '../Data/TravelInfo.db'


class CrawlerBreadth:
    def __init__(self, db_path):
        self.db_helper = DataBaseHelper(db_path)

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

    def get_subsite_url(self, root_url):
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
            # self.db_helper.insert_into_subsite(item['href'], item.get_text(strip=True))
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

    def get_details_url(self, route_list_url):
        """
        抓取列表页详细url,并存入数据库,如：http://www.tuniu.com/tour/210052165
        :param route_list_url: 路线列表页url,如http://www.tuniu.com/guide/v-pts-8501/?pcat=5882
        :return:
        """
        route_id_regex = re.compile(r'http://www\.tuniu\.com/(?:tour|tours)/(?P<route_id>\d{9})')
        route_id_ret = route_id_regex.findall(self.get_html(route_list_url))
        route_id_set = set(item for item in route_id_ret)

        for item in route_id_set:
            url = 'http://www.tuniu.com/tour/' + item
            self.db_helper.insert_into_routeurl(url)

if __name__ == '__main__':
    clawled_departures = set([u'海城市', u'南充', u'梅河口市', u'焦作', u'古交市', u'麻城市', u'佛山', u'惠安县', u'虎林市', u'丹阳市',
                              u'鹿邑县', u'冷水江市', u'恩施', u'孟州市', u'连州市', u'肥乡县', u'鹤岗',u'合肥', u'江阴', u'安阳',
                              u'东兴市', u'栾城县', u'鸡西', u'阿拉善左旗', u'黑河', u'茂名', u'长汀县', u'海原县', u'黄南', u'都江堰市',
                              u'当阳市', u'阿坝', u'津市市', u'凤凰县', u'辉县市', u'海北', u'揭阳', u'柳州'])  # 记录已抓取的出发地，中断后，词列表中的出发地不再抓取

    crawler_obj = CrawlerBreadth(DB_PATH)

    test_url = 'http://www.tuniu.com/'
    test_departure_url_dict = crawler_obj.get_subsite_url(test_url)
    print 'test_departure_url_dict: %d' % len(test_departure_url_dict)
    print test_departure_url_dict
    left_departure_num = len(test_departure_url_dict)

    # test_dep_des_url_dict = dict()  # {出发地:{目的地:目的地路线列表url}}
    for departure_name, departure_url in test_departure_url_dict.items():
        left_departure_num -= 1
        if departure_name in clawled_departures:
            continue
        print 'Left %d departures, Departure %s: %s ' % (left_departure_num, departure_name, departure_url)
        test_des_url_dict = crawler_obj.get_catalog_url(departure_url)
        print 'test_des_url_dict: %d' % len(test_des_url_dict)
        print test_des_url_dict

        gevent_list = []
        left_destinations_num = len(test_des_url_dict)
        for destination_name, destination_url in test_des_url_dict.items():
            left_destinations_num -= 1
            print 'Departure %s, Left %d destinations, Destination %s: %s' % (departure_name, left_destinations_num, destination_name, destination_url)
            gevent_list.append(gevent.spawn(crawler_obj.get_details_url, destination_url))
            gevent.joinall(gevent_list)

