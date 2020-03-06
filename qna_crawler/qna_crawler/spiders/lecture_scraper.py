import scrapy
from scrapy.selector import Selector
from qna_crawler.items import QnaCrawlerItem

from collections import defaultdict
import sys
import datetime
import time
from fake_useragent import UserAgent
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

json_file_name = "woven-arcadia-269609-12b95dbdd1c3.json"

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

spreadsheet_url = "https://docs.google.com/spreadsheets/d/1YEO-EhcPmtj0r0YJzy-xNF6oVEdb8QHS43Eusck83so/edit#gid=2122150374"

# 스프레스시트 문서 가져오기
doc = gc.open_by_url(spreadsheet_url)

# 시트 선택하기

ua = UserAgent()
co = webdriver.ChromeOptions()
co.add_argument("/Users/yoonhoonsang/Desktop/internet_lecture/qna_crawler/chromedriver")
co.add_argument("log-level=1")
co.add_argument("headless")
co.add_argument("user-agent={}".format(ua.random))
co.add_argument("lang=ko_KR")


# def get_proxies(co=co):
#     driver = webdriver.Chrome(chrome_options=co)
#     driver.get("https://free-proxy-list.net/")
#
#     PROXIES = []
#     proxies = driver.find_elements_by_css_selector("tr[role='row']")
#     for p in proxies:
#         result = p.text.split(" ")
#         if result[-1] == "yes":
#             PROXIES.append(result[0] + ":" + result[1])
#
#     driver.close()
#     return PROXIES
#
#
# ALL_PROXIES = get_proxies()
#
#
# def proxy_driver(PROXIES, co=co):
#     prox = Proxy()
#     pxy = ""
#     if PROXIES:
#         pxy = PROXIES[-1]
#     else:
#         print("--- Proxies used up (%s)" % len(PROXIES))
#         PROXIES = get_proxies()
#
#     prox.proxy_type = ProxyType.MANUAL
#     prox.http_proxy = pxy
#     prox.ssl_proxy = pxy
#
#     capabilities = webdriver.DesiredCapabilities.CHROME
#     prox.add_to_capabilities(capabilities)
#
#     driver = webdriver.Chrome(chrome_options=co, desired_capabilities=capabilities)
#
#     return driver
#

# global page
# page = 1
teacher_dic = {
    "etoos_yhk": "https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200386&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={}",
    "etoos_kww": "https://go3.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200245&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={}",
    "megastudy_jjs": "http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=rimbaud666&tec_nm=%uC870%uC815%uC2DD&tec_type=1&brd_cd=784&brd_tbl=MS_BRD_TEC784&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=134&page={} &chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.24915805251066403",
    "mimac_lmh": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=531&currPage={} ",
    "skyedu": "https://skyedu.conects.com/teachers/teacher_qna/?t_id=jhc01&cat1=1&page={} ",
}


##########################################################################################################
##########################################################################################################
##########################################################################################################

# scrapy crawl ETOOS -a start=2020.02.27 -a till=2020.02.26 -o etoos_ver2.csv
class ETOOSSpider(scrapy.Spider):
    name = "ETOOS"
    allowed_domains = ["etoos.com"]
    start_urls = ["http://www.naver.com"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        day_before_yesterday = yesterday - datetime.timedelta(days=1)
        start_temp = str(yesterday).split('-')
        till_temp = str(day_before_yesterday).split("-")

        self.start = datetime.date(
            int(start_temp[0]), int(start_temp[1]), int(start_temp[2])
        )
        self.till = datetime.date(
            int(till_temp[0]), int(till_temp[1]), int(till_temp[2])
        )

        self.worksheet_name = self.teacher
        self.worksheet = doc.worksheet(self.worksheet_name)

    def parse(self, response):
        print("---- Scraping Starts ----")
        print("---- Scraping of {}".format(str(self.start)))
        page = 1
        date_qna_dic = defaultdict(int)
        running = True

        while running:
            try:
                co.add_argument("user-agent={}".format(ua.random))
                self.browser = webdriver.Chrome(chrome_options=co)
                print('Current Page {}'.format(page))

                base_url = teacher_dic[self.teacher].format(str(page))
                self.browser.get(base_url)

                print("Accessing {}".format(base_url))

                title = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "table.subcomm_tbl_board")
                    )
                )

                print("table element poped up")
                tbody = self.browser.find_element_by_tag_name("tbody")
                rows = tbody.find_elements_by_tag_name("tr")

                for row in rows:
                    row_class = row.get_attribute("class")
                    td_list = row.find_elements_by_css_selector("*")
                    writer = td_list[-2].text

                    if row_class == "notice":
                        continue
                    elif len(writer) > 4:
                        print("This is not a question, but answer")
                        continue

                    text = row.text.split()
                    print("row_sample: {}".format(text))

                    date_value, writer = text[-1], text[-2]
                    print("date_value: {}".format(date_value))

                    if len(date_value) == 10:
                        # date comparison
                        # if bigger than till, smaller than start, pass
                        date_value = date_value.split(".")

                        # date_value = [2020,12,23]
                        # date_value[0] = 2020 / date_value[1] = 12/ date_value[2] = 23

                        date_value = datetime.date(
                            int(date_value[0]), int(date_value[1]), int(date_value[2])
                        )

#                         if date_value <= self.start and date_value >= self.till:
                        if date_value == self.start:
                            date_qna_dic[date_value] += 1
                        elif date_value > self.start:
                            print('out of date-range, over {}'.format(self.start))
                        elif date_value < self.start:
                            print("out of date-range, less {}".format(self.till))
                            running = False
                            break

                page += 1
                print("page {}".format(str(page)))

            except Exception as exp:
                print("Error occurred!!")
                print(exp)
                break

        for date in date_qna_dic:
            print('Final Process...')
            self.worksheet.append_row([str(date), str(date_qna_dic[date])])

            item = QnaCrawlerItem()
            item["date"] = date
            item["qna_count"] = date_qna_dic[date]

            yield item


# scrapy crawl MEGASTUDY -a start=2020-02-27 -a till=2020-02-26 -o MEGASTUDY.csv
class MegaSpider(scrapy.Spider):
    name = "MEGASTUDY"
    allowed_domains = ["megastudy.net"]
    start_urls = ["http://www.naver.com"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        start_temp = str(yesterday).split('-')
        till_temp = self.till.split("/")
        self.start = datetime.date(
            int(start_temp[0]), int(start_temp[1]), int(start_temp[2])
        )
        self.till = datetime.date(
            int(till_temp[0]), int(till_temp[1]), int(till_temp[2])
        )
        self.worksheet_name = self.teacher
        self.worksheet = doc.worksheet(self.worksheet_name)

    def parse(self, response):
        print("---- Scraping Starts ----")
        page = 1
        date_qna_dic = defaultdict(int)
        running = True

        while running:
            try:
                co.add_argument("user-agent={}".format(ua.random))
                self.browser = webdriver.Chrome(chrome_options=co)
                print('Current Page {}'.format(page))

                base_url = "http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=rimbaud666&tec_nm=%uC870%uC815%uC2DD&tec_type=1&brd_cd=784&brd_tbl=MS_BRD_TEC784&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=134&page={} &chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.24915805251066403".format(
                    str(page)
                )
                self.browser.get(base_url)

                print("Accessing {}".format(base_url))

                title = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "div.table_list > table.commonBoardList > tbody > tr.top",
                        )
                    )
                )
                print("table element poped up")

                rows = self.browser.find_elements_by_tag_name("tr")

                for row in rows:
                    row_class = row.get_attribute("class")

                    # notice row has 'top' class, in which we skip those.
                    if row_class == "top":
                        continue

                    text = row.text.split()
                    print("row_sample: {}".format(text))

                    date_value = text[-2]
                    print("date_value: {}".format(date_value))

                    if len(date_value) == 10:
                        # date comparison
                        # if bigger than till, smaller than start, pass
                        date_value = date_value.split("-")

                        # date_value = [2020,12,23]
                        # date_value[0] = 2020 / date_value[1] = 12/ date_value[2] = 23
                        date_value = datetime.date(
                            int(date_value[0]), int(date_value[1]), int(date_value[2])
                        )

                        if date_value <= self.start and date_value >= self.till:
                            date_qna_dic[date_value] += 1
                        elif date_value > self.start:
                            print('out of date-range, over {}'.format(self.start))
                        elif date_value < self.till:
                            print("out of date-range, less {}".format(self.till))
                            running = False
                            break

                page += 1
                print("page {}".format(page))

            except Exception as exp:
                print("Error occurred!!")
                print(exp)
                break

        for date in date_qna_dic:
            print('Final Process...')
            self.worksheet.append_row([str(date), str(date_qna_dic[date])])

            item = QnaCrawlerItem()
            item["date"] = date
            item["qna_count"] = date_qna_dic[date]

            yield item


class SkySpider(scrapy.Spider):
    name = "SKYEDU"
    allowed_domains = ["skyedu.conects.com"]
    start_urls = ["http://www.naver.com"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        start_temp = str(yesterday).split('-')
        till_temp = self.till.split("/")
        self.start = datetime.date(
            int(start_temp[0]), int(start_temp[1]), int(start_temp[2])
        )
        self.till = datetime.date(
            int(till_temp[0]), int(till_temp[1]), int(till_temp[2])
        )
        self.worksheet_name = self.teacher
        self.worksheet = doc.worksheet(self.worksheet_name)

    def parse(self, response):
        print("---- Scraping Starts ----")
        page = 139
        date_qna_dic = defaultdict(int)
        running = True

        while running:
            try:
                co.add_argument("user-agent={}".format(ua.random))
                self.browser = webdriver.Chrome(chrome_options=co)
                print('Current Page {}'.format(page))

                base_url = "https://skyedu.conects.com/teachers/teacher_qna/?t_id=jhc01&cat1=1&page={} ".format(
                    str(page)
                )
                self.browser.get(base_url)
                #                 print(f'Online to {base_url}')
                print("Accessing {}".format(base_url))

                title = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.board-list > table")
                    )
                )
                print("table element poped up")

                tbody = self.browser.find_element_by_tag_name("tbody")
                rows = tbody.find_elements_by_tag_name("tr")

                for row in rows:
                    text = row.text.split()
                    print("row_sample: {}".format(text))

                    date_value, writer = text[-1], text[-2]
                    print("date_value: {}".format(date_value))

                    if len(date_value) == 10:
                        # date comparison
                        # if bigger than till, smaller than start, pass
                        date_value = date_value.split("-")

                        # date_value = [2020,12,23]
                        # date_value[0] = 2020 / date_value[1] = 12/ date_value[2] = 23
                        date_value = datetime.date(
                            int(date_value[0]), int(date_value[1]), int(date_value[2])
                        )

                        if date_value <= self.start and date_value >= self.till:
                            date_qna_dic[date_value] += 1
                        elif date_value > self.start:
                            print('out of date-range, over {}'.format(self.start))
                        elif date_value < self.till:
                            print("out of date-range, less {}".format(self.till))
                            running = False
                            break

                page += 1
                print("page {}".format(page))

            except Exception as exp:
                print("Error occurred!!")
                print(exp)
                break

        for date in date_qna_dic:
            print('Final Process...')
            self.worksheet.append_row([str(date), str(date_qna_dic[date])])

            item = QnaCrawlerItem()
            item["date"] = date
            item["qna_count"] = date_qna_dic[date]
            yield item


class MiMacSpider(scrapy.Spider):
    name = "MIMAC"
    rotate_user_agent = True
    start_urls = ["http://www.naver.com"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        start_temp = str(yesterday).split('-')
        till_temp = self.till.split("/")
        self.start = datetime.date(
            int(start_temp[0]), int(start_temp[1]), int(start_temp[2])
        )
        self.till = datetime.date(
            int(till_temp[0]), int(till_temp[1]), int(till_temp[2])
        )
        self.worksheet_name = self.teacher
        self.worksheet = doc.worksheet(self.worksheet_name)

    def parse(self, response):
        print("---- Scraping Starts ----")
        page = 1
        date_qna_dic = defaultdict(int)
        running = True

        while running:
            try:
                co.add_argument("user-agent={}".format(ua.random))
                self.browser = webdriver.Chrome(chrome_options=co)
                print('Current Page {}'.format(page))
                base_url = "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=531&currPage={} ".format(
                    str(page)
                )

                self.browser.implicitly_wait(5)
                self.browser.get(base_url)
                print("Accessing {}".format(base_url))

                title = WebDriverWait(self.browser, 10).until(
                                    EC.presence_of_element_located(
                                        (By.CSS_SELECTOR, "div.tbltype_list > table")
                                    )
                                )

                # get the rows of table
                tbody = self.browser.find_element_by_tag_name("tbody")
                rows = tbody.find_elements_by_tag_name("tr")
                # iterate through rows

                for row in rows:
                    # text is list, consisted by row data
                    row_class = row.get_attribute("class")
                    td_list = row.find_elements_by_css_selector("*")
                    first_td_class = td_list[0].get_attribute("class")

                    if first_td_class == "noti" or row_class == "reply":
                        continue

                    text = row.text.split()
                    print("row_sample: {}".format(text))

                    date_value, writer = text[-2], text[-1]
                    print("date_value: {}".format(date_value))

                    if len(date_value) == 10:
                        print(date_value)
                        # date comparison
                        # if bigger than till, smaller than start, pass
                        date_value = date_value.split("/")

                        # date_value = [2020,12,23]
                        # date_value[0] = 2020 / date_value[1] = 12/ date_value[2] = 23

                        date_value = datetime.date(
                            int(date_value[0]),
                            int(date_value[1]),
                            int(date_value[2]),
                        )

                        if date_value <= self.start and date_value >= self.till:
                            date_qna_dic[date_value] += 1
                        elif date_value > self.start:
                            print('out of date-range, over {}'.format(self.start))
                        elif date_value < self.till:
                            print("out of date-range, less {}".format(self.till))
                            running = False
                            break

                page += 1
                print("page {}".format(page))

            except Exception as exp:
                print("Error occurred!!")
                print(exp)
                break

        for date in date_qna_dic:
            self.worksheet.append_row([str(date), str(date_qna_dic[date])])

            item = QnaCrawlerItem()
            item["date"] = date
            item["qna_count"] = date_qna_dic[date]
            yield item
