# coding: utf-8

from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib2
import chardet
import re

# headers = {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
#     }
# request = urllib2.Request('http://www.tuniu.com/guide/d-dali-3306/?pcat=82', headers=headers)
# response = urllib2.urlopen(request)  # 超时设置
# result = response.read()
# with open('test.html', 'w') as f:
#     f.write(result)

# soup = BeautifulSoup(result, 'html5lib')
# div_list = soup.find_all('a', attrs={'href': 'True'})
# print len(div_list)
# for item in div_list:
#     print item

# detail_url_regex = re.compile(r'http://www\.tuniu\.com/(?:tour|tours)/\d{9}')
# detail_url_ret = detail_url_regex.findall(result)
# detail_url_set = set(item for item in detail_url_ret)
# print len(detail_url_set)
# print detail_url_set

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

dep_des_url = {'hangzhou': {'shanghai': 'http://www.tuniu.com/guide/d-dali-3306/?pcat=82'},
               'hangzhou1': {'shanghai1': 'http://www.tuniu.com/guide/d-dali-3306/?pcat=821'}}
for dep_item, des_url_dict_item in dep_des_url.items():
    for des_item, url_item in des_url_dict_item.items():
        print url_item
