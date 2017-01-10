# coding: utf-8
# author: luyf
# create date: 2017.01.05

import sqlite3

database1 = sqlite3.connect('./Crawler/travel_info.db')
cursor1 = database1.cursor()
cursor1.execute('select * from urllistold')
url_list = cursor1.fetchall()
cursor1.close()
database1.close()
database2 = sqlite3.connect('./Database/TravelInfo.db')
cursor2 = database2.cursor()
for item in url_list:
    cursor2.execute("insert into urllist(url) values('%s')" % item)
database2.commit()
cursor2.close()
database2.close()
