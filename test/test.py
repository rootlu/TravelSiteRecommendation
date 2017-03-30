# coding: utf-8

from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib2
import re
import HTMLParser
import json
import sqlite3

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
}
request = urllib2.Request('http://vacations.ctrip.com/tours/d-sanfrancisco-249', headers=headers)
response = urllib2.urlopen(request)  # 超时设置
result = response.read()
with open('test.html', 'w') as f:
    f.write(result)

# comment_url = 'http://www.tuniu.com/papi/product/remarkList?refresh=1&productId=210051158&productType=1&page=1'   
# result = ''
# comment_json = json.loads(result)
# print comment_json['data']['totalPages']

# soup = BeautifulSoup(result, 'html5lib')
# tag_summary = soup.find('div', attrs={'class': 'resource-section-content-inner'})
# # print tag_summary
# print re.sub(r'\n+|\t+|\s+|\r', '', tag_summary.get_text()) if tag_summary is not None else None
#

# script_regex = re.compile(r'window\.pageData[\S\s]+?departCityInfo":(?P<route_departure>.*?),"backCityInfo', re.M)
# script_ret = script_regex.search(result)
# print script_ret.group()
# route_departure_list = json.loads(script_ret.group('route_departure'))
# print route_departure_list
# for item in route_departure_list:
#     print item['name']
#     print item['price']
#     print item['code']

# html_parser = HTMLParser.HTMLParser()
# title = soup.title.get_text() if soup.title.get_text() is not None else '_'
# title = html_parser.unescape(title).split('_')[0]
# print title
#
# tag_grade_list = soup.find_all('a', attrs={'class': 'resource-statisfaction-number'})
# print tag_grade_list[0].get_text(strip=True)[:-1] if tag_grade_list is not None else 0
#
# tag_detail_list = soup.find_all('div', attrs={'class': 'detail-sections'})
# print re.sub(r'\n+|\t+|\s+|\r', '', tag_detail_list[0].get_text(strip=True))

# url = 'http://www.tuniu.com/tour/210051158'
# route_id = url[-9:]
# comment_url = 'http://www.tuniu.com/papi/product/remarkList?refresh=1&productId='+route_id+'&productType=1&page=1'
# request = urllib2.Request(comment_url)
# response = urllib2.urlopen(request)
# print response.read()

# tag_favor_list = soup.find_all('div', attrs={'class': 'J_DetailFavor'})
# # print tag_favor_list[0].get_text().strip()
# print re.sub(r'\n+|\t+|\s+|\r', '', tag_favor_list[0].get_text().strip())
#
# tag_feature_list = soup.find_all('div', attrs={'class': 'J_DetailFeature'})
# print re.sub(r'\n+|\t+|\s+|\r', '', tag_feature_list[0].get_text().strip())
#
# tag_route_list = soup.find_all('div', attrs={'class': 'J_DetailRoute'})
# print re.sub(r'\n+|\t+|\s+|\r', '', tag_route_list[0].get_text().strip())

# tag_fee_list = soup.find_all('div', attrs={'class': 'J_DetailFee'})
# print len(tag_fee_list)
# print re.sub(r'\n+|\t+|\s+|\r', '', tag_fee_list[0].get_text().strip())


# detail_url_regex = re.compile(r'http://www\.tuniu\.com/(?:tour|tours)/\d{9}')
# detail_url_ret = detail_url_regex.findall(result)
# detail_url_set = set(item for item in detail_url_ret)
# print len(detail_url_set)
# print detail_url_set

xiecheng_detail_url_regex = re.compile(r'<a href="(?P<route_url>http://vacations.ctrip.com/(?:grouptravel|freetravel)/p\w+\.html[\S\s]+?)"')
detail_url_ret = xiecheng_detail_url_regex.findall(result)
detail_url_set = set(item for item in detail_url_ret)
print detail_url_set

# soup = BeautifulSoup(str(div_list[0]), 'html5lib')
# test_dict = {}
# test_list = soup.find_all('a', attrs={'href': True})
# print len(test_list)
# print test_list
#
# test_set = set(filter(lambda x: x['href'].startswith('http://'), test_list))
# print len(test_set)
# print test_set

# for item in test_set:
#     print item.get_text(strip=True)
# test_dict[item['title']] = item['href']

# # print len(test_dict)
# # print test_dict
# for (departure, departure_url) in test_dict.items():
#     print departure_url

# dep_des_url = {'hangzhou': {'shanghai': 'http://www.tuniu.com/guide/d-dali-3306/?pcat=82'},
#                'hangzhou1': {'shanghai1': 'http://www.tuniu.com/guide/d-dali-3306/?pcat=821'}}
# for dep_item, des_url_dict_item in dep_des_url.items():
#     for des_item, url_item in des_url_dict_item.items():
#         print url_item
#
# detail_url_regex = re.compile(r'http://www\.tuniu\.com/(?:tour|tours)/(?P<route_id>\d{9})')
# detail_url_ret = detail_url_regex.findall('<link rel="stylesheet" type="text/css" href="http://www.tuniu.com/tour/201610182/common/fil</title>')
# print detail_url_ret
# detail_url_set = set(item for item in detail_url_ret)
# for item in detail_url_set:
#     print item
#     url = 'http://www.tuniu.com/tour/'+item
#     print url

# database = sqlite3.connect('../Data/TravelInfo.db')
# cursor = database.cursor()
# table_name = 'urllist'
# file_id = 'url'
# value = 'http://www.tuniu.com/tours/21'
# command_0 = 'select * from routeurl'
# command = "select rowid from %s where %s = '%s'" % (table_name, file_id, value)
# cursor = cursor.execute(command_0)
# result = cursor.fetchall()
# url_list = []
# for item in result:
#     url_list.append(item[0])
# print url_list
# print result[0] if result is not None else None
# route_info = {'sad':'sdsd\'ssdd', 'sd':'123'}
# for i in route_info:
#     route_info[i] = route_info[i].replace('\'', '\"')
# print route_info
# url = 'http://www.tuniu.com/papi/product/remarkList?refresh=1&productId=213123123&productType=1&page='
# route_id_regex = re.compile(r'^http\S*?productId=(?P<route_id>\d{9})')
# route_id_ret = route_id_regex.search(url)
# error_url = 'http://www.tuniu.com/tour/' + route_id_ret.group('route_id')
# print error_url
