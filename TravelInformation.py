# coding:utf-8
# author: luyf
# create date: 2016.12.14

import urllib2
from bs4 import BeautifulSoup
import re
import time
import MySQLdb
import chardet
from TravelWeb2.Net import searchengine
import sys  # 要重新载入sys。因为 Python 初始化后会删除 sys.setdefaultencoding 这个方 法

reload(sys)
sys.setdefaultencoding('utf-8')


# 获取所有url
class GETURL:
    def __init__(self, url):
        self.url_list = []
        self.URL = url
        self.cityNameList = []
        self.cityUrlList = []
        username = "root"
        password = "a09317999011"
        dbname = "test"
        # 打开数据库连接
        self.db = MySQLdb.connect("localhost", username, password, dbname, charset="utf8")
        # 使用cursor()方法获取操作游标
        self.cursor = self.db.cursor()
        self.cursor.execute('select max(id) from route')
        self.insert_num = self.cursor.fetchone()[0]
        if None == self.insert_num:
            self.insert_num = 0

    def __del__(self):
        self.db.close()

    # 获取网页源码
    def getPage(self, url):
        #         enable_proxy = True
        #         proxy_handler = urllib2.ProxyHandler({"http":'http://113.68.87.72:8090'})
        #         null_proxy_handler = urllib2.ProxyHandler({})
        #         if enable_proxy:
        #             opener = urllib2.build_opener(proxy_handler)
        #         else:
        #             opener = urllib2.build_opener(null_proxy_handler)
        #         urllib2.install_opener(opener)
        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request, timeout=5)  # 超时设置
            result = response.read()
            chardit = chardet.detect(result[:1000])
            print chardit
            result = result.decode(chardit['encoding'], 'ignore').encode('utf-8')
            return result
        except:
            return None

    # 获取所有城市及对应的url
    def getCityList(self, html_page):

        soup = BeautifulSoup(html_page, 'html5lib', fromEncoding='utf8')  #
        cityPage_div = soup.find_all('div', class_='sel_list')
        cityPageList = cityPage_div[0].find_all('a')  # 获取所有url
        length = len(cityPageList)
        for i in range(length):
            cityUrl = 'http://vacations.ctrip.com/' + cityPageList[i].attrs['href'].replace("you",
                                                                                            "tours")  # 修正每个城市对应的url
            cityName = cityPageList[i].attrs['title']  # 获取城市名
            self.cityUrlList.append(cityUrl)
            self.cityNameList.append(cityName)

    # 获取某一地点的所有分页url
    def getUrlList(self, html_page):
        soup = BeautifulSoup(html_page, 'html5lib', fromEncoding='utf8')
        urlListPage = []
        if soup:
            # 正则匹配分页栏
            pattern = re.compile('<div id="_pg" class=\"pkg_page basefix\">.*?<a .*? href=\"(.*?)\".*?>.*?</div>', re.S)
            firstUrl = re.search(pattern, htmlPage)
            #             print firstUrl
            if (firstUrl):
                urlNum_div = soup.find_all('div', class_='pkg_page basefix')  # 获取含有url数量的标签
                #                 urlHead=re.findall(re.compile('(.*?)#.*?'), firstUrl.group(1).strip())#第一页的url
                urlHead = firstUrl.group(1).strip()
                urlNum = urlNum_div[0].contents[-6].getText()  # 分离数字和汉字
                for i in range(int(urlNum)):
                    # 修正路线列表页url
                    urlPageList.append(
                        "http://vacations.ctrip.com" + urlHead + "/p" + str(i + 1) + "#searchFilterContainer")

        return urlPageList

    def getUrl(self, html_page):
        soup = BeautifulSoup(html_page, 'html5lib', fromEncoding='utf8')
        self.url_list = []
        if soup:
            resultUrl = soup.find_all('a', class_='small_title')
            # 提取对每一个链接标签中的链接，并保存到url_list
            for i in range(len(resultUrl)):
                if ("http://" in resultUrl[i].attrs['href']):
                    continue
                else:
                    trueUrl = "http://vacations.ctrip.com" + resultUrl[i].attrs['href']
                    self.url_list.append(trueUrl)
        return self.url_list

    # 解析详细路线页面
    def information(self, url_list, destination):
        length = len(self.url_list)
        print "a page urlList：%d" % length
        for i in range(length):
            print self.url_list[i]
            # 该路线不存在，存至数据库
            if (not self.judgeRepeat(self.url_list[i])):
                i_html_page = self.getPage(self.url_list[i])
                if (i_html_page):
                    soup = BeautifulSoup(i_html_page, 'html5lib', fromEncoding='utf8')
                    contents = []
                    if soup:
                        # 旅游路线名称
                        if (soup.title):
                            content = soup.title.string
                            contents.append(content)
                        else:
                            contents.append("路线")
                        # 获取路线编号
                        num_li1 = soup.find_all("li", attrs={"class": "product_num"})
                        num_li2 = soup.find_all("p", attrs={"class": "detail_number"})
                        if (num_li1):
                            num = num_li1[0].getText()
                            contents.append(num)
                        else:
                            if (num_li2):
                                num = num_li2[0].getText()
                                contents.append(num)
                            else:
                                num = "未知id"
                                contents.append(" ")

                        # 出发地
                        pattern_city = re.compile('<script>.*?StartCityName: \'(.*?)\'.*?</script>', re.S)
                        city = re.search(pattern_city, i_html_page)
                        if (city):
                            content = city.group(1).strip()
                        else:
                            content = "南京"
                        contents.append(content)
                        #                 print city.group(1).strip()

                        # 价格
                        pattern_price = re.compile('<script>.*?\"minPrice\":(.*?)\,.*?\}.*?</script>', re.S)
                        price = re.search(pattern_price, i_html_page)
                        if (price):
                            content = price.group(1)
                            if (content == "实时计价"):
                                content = "0"
                        else:
                            price = "0"
                        contents.append(content)
                        #                 print price.group(1).strip()

                        # 评分
                        score_a = soup.find_all("a", class_="score")
                        if (score_a):
                            content = score_a[0].getText()
                            contents.append(content)
                        else:
                            contents.append('3.0 分')  # 无评分，取3

                        # 图片url
                        pattern_pic = re.compile('<img.*?_src=\"(.*?)\".*?', re.S)
                        pic = re.search(pattern_pic, i_html_page)
                        if (pic):
                            picUrl = pic.group(1)
                        else:
                            picUrl = "http://images4.c-ctrip.com/target/hotel/7000/6938/0968466fbec349d2ad2d9ab76821c0e1_550_412.jpg";
                        contents.append(picUrl)

                        # 联系方式/供应商
                        phone_dl = soup.find_all("dl", class_="provider_info" + "\n")
                        if (phone_dl):
                            content = phone_dl[0].getText()
                            contents.append(content)
                        else:
                            contents.append(" ")

                        # 景点
                        point_div = soup.find_all("div", attrs={"id": "simple_route_div"})
                        if (point_div):
                            content = point_div[0].getText()
                            contents.append(content)
                        else:
                            contents.append(" ")

                        # 行程
                        route_div = soup.find_all("div", id="js_detail_travelCtrip")
                        if (route_div):
                            content = ''.join(route_div[0].getText().split())
                            contents.append(content)
                        else:
                            contents.append(" ")

                        # 经理推荐
                        recommend_div = soup.find_all('div', class_='pm_recommend')
                        if (recommend_div):
                            content = recommend_div[0].getText()
                            contents.append(content)
                        else:
                            contents.append(" ")

                        # 详细信息汇总
                        detail_div = soup.find_all('div', class_='under_tab_detail')
                        if (detail_div):
                            contents.append(content.replace('\n', ''))
                        else:
                            contents.append(' ')

                        if (num != u"未知id"):
                            self.saveToDB(contents, self.url_list[i], destination)
                            self.insert_num += 1
                            self.db.commit()
                    else:
                        print "soup is None"
        print u"one route has finshed!"
        self.db.commit()

    # 判断该路线是否存在
    def judgeRepeat(self, url):

        sql = "SELECT id FROM route where route_url='%s'" % url
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            if result != None:
                return True
        except:
            print "Error: unable to fecth data"

        return False

    def saveToDB(self, contents, routeUrl, routeDestination):

        # sql语句
        #         sql_size=cursor.execute("select * from traveltable")
        #         print "SQL size:%d" %sql_size
        routeNum = contents[1][3:]
        routeDeparture = contents[2]
        routeName = contents[0]
        routePrice = float(contents[3])
        routeScore = float(contents[4][:3])
        routePic = contents[5]
        routeMessage = ''.join(contents[6:])
        try:
            sql = "INSERT INTO route(NUM,NAME,ROUTE_URL,DEPARTURE,DESTINATION,PRICE,SCORE,MESSAGE,IMG) \
            VALUES ('%s','%s','%s','%s','%s',%f,%f,'%s','%s')" % \
                  (routeNum, routeName, routeUrl, routeDeparture, routeDestination, routePrice, routeScore,
                   routeMessage[:150], routePic)
            #         (routeNum,routeName,routeUrl,routeDeparture,routeDestination,routePrice,routeScore,routeMessage,routePic)
            self.cursor.execute(sql)
            self.insert_num += 1
        # print "db success"
        except MySQLdb.Error, e:
            print "MySQL Error:%s" % e
            return
        except UnicodeDecodeError, e:
            print "UnicodeDecodeError Error:%s" % e
            return
        Searchengine = searchengine.get_staion_url()
        Searchengine.crawl(self.insert_num, routeName, routeMessage);

    # main函数
    def main(self):
        # 获取第一个页面的所有城市url及名称
        indexPage = self.getPage(self.URL)  #
        if (indexPage):
            self.getCityList(indexPage)
            # 第一层循环，遍历全国城市url
            length = len(self.cityUrlList)
            print length
            for i in range(length):
                print self.cityNameList[i]
                aCityPage = self.getPage(self.cityUrlList[i])
                if (aCityPage):
                    aCityUrlPage = self.getUrlList(aCityPage)  # 某城市分页的url
                    # 第二层，遍历某一城市所有分页路线
                    for item in aCityUrlPage:
                        print item
                        html_page = self.getPage(item)
                        # 该页的某一路线
                        if (html_page):
                            littleUrl = self.getUrl(html_page)
                            self.information(littleUrl, self.cityNameList[i])
                        else:
                            continue
                else:
                    continue


url = 'http://vacations.ctrip.com/tours'
sanya = GETURL(url)
sanya.main()
