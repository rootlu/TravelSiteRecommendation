# coding:utf-8
# author: luyf
# create date: 2016.12.25
import HTMLParser

from bs4 import BeautifulSoup
# from multiprocessing import Process
import re
from gevent import monkey; monkey.patch_all()
import gevent
import jieba
import json
import time
import sys
sys.path.append("..")
from Database.DataBaseHelper import *
from Request.RequestHelper import *
from CrawlerLastUrl import *


# 构造一个单词列表，这些单词被忽略
IGNORE_WORDS = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it',
                    u'是', u'的', u'它', u'他', u'她', u'也', u'你', u'我',
                    u'优惠信息', u'产品特色', u'线路介绍', u'费用说明', u'预定须知', u'线路导游', u'游客点评', u'在线问答', u'相关产品'])
PROCESS_URL_NUM = 3000  # 每3000条url，创建一个进程
DB_PATH = '../Data/TravelInfo.db'


class CrawlerData:
    def __init__(self, db_path):
        self.request_helper = RequestHelper()
        self.db_helper = DataBaseHelper(db_path)

    def get_route_info(self, url_list):
        """
        获取路线详细信息，插入数据库
        :param url_list:路线url列表
        :return:
        """
        for url in url_list:
            url_id = self.db_helper.is_exist('routeurl', 'url', url)  # 查询urllist中url对应的id
            print 'Information: %d ' % url_id
            detail_page_html = self.request_helper.send_request(url)
            if detail_page_html == '':
                continue

            soup = BeautifulSoup(detail_page_html, 'html5lib')
            # 路线详细信息
            route_info_dict = {'title': '', 'satisfaction': '0', 'summary': '', 'text': ''}
            # 路线标题
            html_parser = HTMLParser.HTMLParser()
            route_name = soup.title.get_text(strip=True) if soup.title is not None else '_'
            route_info_dict['title'] = html_parser.unescape(route_name).split('_')[0]
            # 总体评分
            tag_grade = soup.find('a', attrs={'class': 'resource-statisfaction-number'})
            route_info_dict['satisfaction'] = tag_grade.get_text(strip=True)[:-1] if tag_grade is not None else '0'
            # 行程概要
            tag_summary = soup.find('div', attrs={'class': 'resource-section-content-inner'})
            route_info_dict['summary'] = re.sub(r'\n+|\t+|\s+|\r', '', tag_summary.get_text(strip=True)) if tag_summary is not None else ''
            # 路线详细信息
            tag_detail = soup.find('div', attrs={'class': 'detail-sections'})
            route_info_dict['text'] = re.sub(r'\n+|\t+|\s+|\r', '', tag_detail.get_text(strip=True)) if tag_detail is not None else ''
            # 插入新数据到数据表 routeinfo
            route_info_dict = self.normalize_sql(route_info_dict)  # 规范化sql语句，剔除数据中可能存在的单引号
            self.db_helper.insert_into_routeinfo(url_id, route_info_dict['title'], int(route_info_dict['satisfaction']), route_info_dict['summary'], route_info_dict['text'])

            # 路线出发城市及价格信息
            self.get_route_departure(url_id, detail_page_html)

            # 路线评论数据
            self.get_route_comment(url_id, url)

    def normalize_sql(self, route_info):
        """
        规范化sql语句，防止插入数据中存在的单引号造成sql语法错误
        :param route_info: 字典
        :return:
        """
        for i in route_info:
            route_info[i] = route_info[i].replace('\'', '\"')
        return route_info

    def get_route_departure(self, urlid, page_html):
        """
        获取路线出发城市及价格信息，并插入到数据库表routedep
        :param urlid
        :param page_html:
        :return:
        """
        # 路线出发地及价格信息， 不同出发地，价格不同
        script_regex = re.compile(r'window\.pageData[\S\s]+?departCityInfo":(?P<route_departure>.*?),"backCityInfo',
                                  re.M)
        script_ret = script_regex.search(page_html)
        if script_ret is not None:
            route_departure_list = json.loads(script_ret.group('route_departure'))
            if route_departure_list is not None:
                for item in route_departure_list:
                    route_departure = item['name'] if item['name'] is not None else 'UNKNOWN'
                    route_price = int(item['price']) if item['price'] is not None else 0
                    self.db_helper.insert_into_routedep(urlid, route_departure, route_price)

    def get_route_comment(self, url_id, url):
        """
        请求路线评论json数据
        :param url_id
        :param url:
        :return:
        """
        route_id = url[-9:]
        route_comment = {'outline_comment': '', 'detail_comment': ''}
        outline_comment_url = 'http://www.tuniu.com/papi/product/remarkStatus?refresh=1&productId=' + route_id + '&productType=1'
        route_comment['outline_comment'] = self.request_helper.send_request(outline_comment_url)

        detail_1_comment_url = 'http://www.tuniu.com/papi/product/remarkList?refresh=1&productId=' + route_id + '&productType=1&page=1'
        page_1_comment = self.request_helper.send_request(detail_1_comment_url)
        if page_1_comment == '':
            self.db_helper.insert_into_routecom(url_id, route_comment['outline_comment'], '')
        else:
            comment_json = json.loads(page_1_comment)
            try:
                total_pages = comment_json['data']['totalPages']
            except:
                return
            for i in range(total_pages):
                detail_comment_url = 'http://www.tuniu.com/papi/product/remarkList?refresh=1&productId=' + route_id + '&productType=1&page=' + str(i+1)
                route_comment['detail_comment'] = self.request_helper.send_request(detail_comment_url)
                # comment_json = json.load(comment_page)
                route_comment = self.normalize_sql(route_comment)
                self.db_helper.insert_into_routecom(url_id, route_comment['outline_comment'], route_comment['detail_comment'])

    # def get_text_only(self, soup):
    #     """
    #     从一个HTML网页中获取文字（不带标签的）,递归向下的方式获取网页中的文字，保留了文字出现的前后顺序
    #     :param soup: 含有标签的网页
    #     :return:网页中的文字
    #     """
    #     text = soup.string  # 只有一个子节点的时候，获取第该节点的内容，否则返回None
    #     if text is None:
    #         next_contents = soup.contents  # 返回该节点的子节点列表
    #         result_text = ''
    #         for content_item in next_contents:
    #             sub_text = self.get_text_only(content_item)
    #             result_text += sub_text + '\n'
    #         return result_text
    #     else:
    #         return text.strip()  # 移除字符串头尾指定的字符，默认为空格

    # def separte_words(self, text):
    #     """
    #     根据任何非空白字符进行分词处理,将字符串拆分成一组独立的单词
    #     :param text: 待拆分的字符串
    #     :return: 单词list
    #     """
    #     result_list = []
    #     splitter = re.compile(ur'[^a-zA-Z0-9_\u4e00-\u9fa5]')  # python2.7中要使用‘ur’匹配任意不是字母，数字，下划线，汉字的字符
    #     for s in splitter.split(text):  # 使用结巴分词，处理中文分词
    #         if s != '':
    #             result_list.extend(jieba.lcut(s.lower()))
    #     return result_list

    # def process_start(self, tasks):
    #     """
    #     启动进程，使用协程来执行
    #     :param tasks:
    #     :return:
    #     """
    #     gevent_task_list = []  # 存放协程任务
    #     for item in tasks:
    #         gevent_task_list.append(gevent.spawn(self.get_route_info, item))
    #     gevent.joinall(gevent_task_list)

    def crawl_data(self, route_url_list, process_url_num=PROCESS_URL_NUM):
        """
        循环遍历网页列表，针对每个网页调用add_to_index函数，添加索引。
        利用BeautifulSoup抓取网页中的数据
        :param route_url_list:路线url列表
        :param process_url_num: 每process_url_num条url创建一个进程
        :return:
        """
        url_count = 0  # 计数器，记录添加到协程队列的url数目
        task_list = []
        gevent_list = []
        for route_url_item in route_url_list:
            url_count += 1
            task_list.append(route_url_item)
            if url_count == process_url_num:
                # p = Process(target=self.process_start, args=(task_list,))
                # p.start()
                gevent_list.append(gevent.spawn(self.get_route_info, task_list))
                task_list = []  # 重置任务队列
                url_count = 0  # 重置计数器
        if len(task_list) != 0:  # 若退出循环后任务队列里还有url剩余
            # p = Process(target=self.process_start, args=(task_list,))  # 把剩余的url全都放到最后这个进程来执行
            # p.start()
            gevent_list.append(gevent.spawn(self.get_route_info, task_list))
        gevent.joinall(gevent_list)

if __name__ == '__main__':
    crawler_obj = CrawlerData(DB_PATH)

    total_url_list = [x[0] for x in crawler_obj.db_helper.select_all_data('routeurl', 'ALL')]
    crawler_obj.crawl_data(total_url_list)  # 首次运行程序，抓取routeurl中的url
    time.sleep(15)

    # 二次爬取请求出错的数据
    errors_list = [x[0] for x in crawler_obj.db_helper.select_all_data('routeurl', 'ALL')]
    crawler_obj.crawl_data(errors_list, process_url_num=len(errors_list)/20)

    # 爬取剩余url
    crawler_last_url_obj = CrawlerLastUrl(DB_PATH)
    last_url_list = crawler_last_url_obj.get_last_url()
    print len(last_url_list)
    crawler_obj.crawl_data(last_url_list, process_url_num=len(last_url_list)/20)

    # TODO:  数据库查询插入效率，事务机制

