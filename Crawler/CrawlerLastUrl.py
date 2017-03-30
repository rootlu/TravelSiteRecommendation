# coding: utf-8
# author: luyf
# create date: 2017.02.19

import sys
sys.path.append("..")
from Database.DataBaseHelper import *

DB_PATH = '../Data/TravelInfo.db'


class CrawlerLastUrl:

    def __init__(self, db_path):
        self.db_helper = DataBaseHelper(db_path)

    def get_last_url(self):
        url_nums = self.db_helper.get_table_count('routeurl')
        total_url_id = [x+1 for x in range(url_nums)]
        has_crawled_url_id = [x[0] for x in self.db_helper.select_all_data('routeinfo', 'urlid')]
        last_url_id = list(set(total_url_id) ^ set(has_crawled_url_id))
        last_url_list = []
        for item in last_url_id:
            last_url_list.extend([x[0] for x in self.db_helper.select_one_data('url', 'routeurl', 'rowid', item)])
        return last_url_list
#
# if __name__ == '__main__':
#     crawler_last_data_obj = CrawlerLastUrl(DB_PATH)
#     last_url = crawler_last_data_obj.get_last_url()
#     print last_url
#     print len(last_url)
