# coding: utf-8
# author: luyf
# create date: 2017.01.08
import urllib2
import time
import re
import sys
sys.path.append("..")
from Database.DataBaseHelper import *


class RequestHelper:
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }
        self.timeout = 10

    def send_request(self, url):
        """
        发送请求，获取url页面html
        :param url:
        :return: 响应html
        """
        try:
            request = urllib2.Request(url, headers=self.header)
            response = urllib2.urlopen(request, timeout=self.timeout)  # 超时设置
            result = response.read()
            time.sleep(3)
            return result
        except Exception:
            print '---Request %s Error!---' % url
            if len(url) > 36:  # 评论请求出错，截取路线id
                route_id_regex = re.compile(r'^http\S*?productId=(?P<route_id>\d{9})')
                route_id_ret = route_id_regex.search(url)
                url = 'http://www.tuniu.com/tour/' + route_id_ret.group('route_id')
            db_helper = DataBaseHelper('../Data/TravelInfo.db')  # 数据库路径写死了
            db_helper.insert_into_routeerrorurl(url)
            return ''
