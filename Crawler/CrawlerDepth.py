# coding: utf-8
# author: luyf
# create date: 2017.01.08
import re
from bs4 import BeautifulSoup
from urlparse import urljoin
from gevent import monkey; monkey.patch_all()
import gevent
import sys
sys.path.append("..")
from Database.DataBaseHelper import *
from Request.RequestHelper import *

CRAWLER_DEPTH = 5  # 爬虫深度
DB_PATH = '../Data/TravelInfo.db'

class CrawlerDepth:
    def __init__(self, db_path):
        self.request_helper = RequestHelper()
        self.db_helper = DataBaseHelper(db_path)

    def get_detail_url(self, url):
        """
        从当前url网页中，通过正则匹配路线url
        :param url:
        :return:
        """
        detail_url_html = self.request_helper.send_request(url)
        detail_url_id_regex = re.compile(r'http://www\.tuniu\.com/(?:tour|tours)/(?P<route_id>\d{9})')
        detail_url_id_ret = detail_url_id_regex.findall(detail_url_html)
        detail_url_id_set = set(item for item in detail_url_id_ret)

        for item in detail_url_id_set:
            url = 'http://www.tuniu.com/tour/' + item
            self.db_helper.insert_into_routeurl(url)

    def crawler_depth(self, root_url, depth=CRAWLER_DEPTH):
        """
        爬虫函数，利用BeautifulSoup抓取网页中的所有链接，将这些链接添加到new_pages集合中
        一定深度循环结束之前，将new_page赋给pages,这一过程再次循环，知道depth结束
        :param root_url: 根站点 列表
        :param depth: 爬虫深度
        :return:
        """
        for k in range(depth):
            print 'Depth: %d' % k
            new_url = set()
            for root_url_item in root_url:
                url_html = self.request_helper.send_request(root_url_item)
                if url_html == '':
                    continue
                else:
                    soup = BeautifulSoup(url_html, 'lxml')
                links = soup.find_all('a')  # 找到所有超链接标签
                for link in links:
                    if 'href' in dict(link.attrs):  # 获取link的属性字典
                        url = urljoin(root_url_item, link['href'])  # 从相对路径获取绝对路径, page+相对路径地址
                        if url.find("'") != -1:  # 存在不合法字符
                            continue
                        url = url.split('#')[0]  # 去掉位置部分
                        if url[0:4] == 'http':
                            new_url.add(url)
                        self.get_detail_url(url)  # 正则匹配当前 页面中所有符合路线详细信息url规则的链接
            root_url = new_url

if __name__ == '__main__':
    crawler_obj = CrawlerDepth(DB_PATH)
    url_list = ['http://www.tuniu.com/']
    thread_num = 20
    gevent_cor = gevent.spawn(crawler_obj.crawler_depth, url_list)  # 协程
    gevent_cor.join()

