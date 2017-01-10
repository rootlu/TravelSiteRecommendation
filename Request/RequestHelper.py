# coding: utf-8
# author: luyf
# create date: 2017.01.08
import urllib2
import time


class RequestHelper:
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }
        self.timeout = 5

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
            print 'Request Error!'
            return ''
