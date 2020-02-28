import scrapy
from scrapy.selector import Selector
from qna_crawler.items import QnaCrawlerItem

from collections import defaultdict
import sys
import datetime
import time
from fake_useragent import UserAgent
import random

from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

ua = UserAgent()
co = webdriver.ChromeOptions()
co.add_argument("log-level=3")
co.add_argument("headless")
co.add_argument(f"user-agent={ua.random}")
co.add_argument("lang=ko_KR")


def get_proxies(co=co):
    driver = webdriver.Chrome(chrome_options=co)
    driver.get("https://free-proxy-list.net/")

    PROXIES = []
    proxies = driver.find_elements_by_css_selector("tr[role='row']")
    for p in proxies:
        result = p.text.split(" ")
        if result[-1] == "yes":
            PROXIES.append(result[0]+":"+result[1])

    driver.close()
    return PROXIES

ALL_PROXIES = get_proxies()

def proxy_driver(PROXIES, co=co):
    prox = Proxy()

    if PROXIES:
        pxy = random.choice(PROXIES)
    else:
        print("--- Proxies used up (%s)" % len(PROXIES))
        PROXIES = get_proxies()

    prox.proxy_type = ProxyType.MANUAL
    prox.http_proxy = pxy
    prox.ssl_proxy = pxy

    capabilities = webdriver.DesiredCapabilities.CHROME
    prox.add_to_capabilities(capabilities)

    driver = webdriver.Chrome(chrome_options=co, desired_capabilities=capabilities)

    return driver

# scrapy crawl ETOOS -a start=2020.02.27 -a till=2020.02.26 -o etoos_ver2.csv
class ETOOSSpider(scrapy.Spider):
    name = "ETOOS"
    allowed_domains = ['etoos.com']

    start_urls = [
        'http://www.naver.com'
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        start_temp = self.start.split('.')
        till_temp  = self.till.split('.')
        self.start = datetime.date(int(start_temp[0]), int(start_temp[1]), int(start_temp[2]))
        self.till  = datetime.date(int(till_temp[0]), int(till_temp[1]), int(till_temp[2]))

    def parse(self, response):
        print('---- Scraping Starts ----')
        page = 1
        base_url = f'https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200386&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={str(page)}'
        date_qna_dic = defaultdict(int)
        running = True

        while running:
            try:
                co.add_argument(f"user-agent={ua.random}")
                self.browser = webdriver.Chrome(chrome_options = co)

                base_url = f'https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200386&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={str(page)}'

                self.browser.get(base_url)
                print(f'Online to {base_url}')

                title = WebDriverWait(self.browser, 10) \
                                        .until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.subcomm_tbl_board")))
                print('table element poped up')

                rows = self.browser.find_elements_by_tag_name('tr')
                rows = rows[4:]

                for row in rows:
                    text = row.text.split()
                    print(f'row_sample: {text}')

                    date_value, writer = text[-1], text[-2]
                    print(f'date_value: {date_value}')
                    print(f'writer: {writer}')

                    if len(date_value) == 10:
                        print(date_value)
                        # date comparison
                        # if bigger than till, smaller than start, pass
                        date_value = date_value.split('.')

                        # date_value = [2020,12,23]
                        # date_value[0] = 2020 / date_value[1] = 12/ date_value[2] = 23

                        date_value = datetime.date(int(date_value[0]), int(date_value[1]), int(date_value[2]))


                        if date_value <= self.start and date_value >= self.till:
                            if writer not in ['연구실', '선생님', '작성자']:
                                date_qna_dic[date_value] += 1
                                print(f'{date_value}:{date_qna_dic[date_value]}')

                        else:
                            print('out of date-range')
                            running = False
                            break

                page += 1
                print(f'page {page}')

            except Exception as exp:
                print('Error occurred!!')
                print(exp)
                break



        for date in date_qna_dic:
            item = QnaCrawlerItem()
            item['date'] = date
            item['qna_count'] = date_qna_dic[date]
            yield item

# scrapy crawl MEGASTUDY -a start=2020-02-27 -a till=2020-02-26 -o MEGASTUDY.csv
class MegaSpider(scrapy.Spider):
    name = "MEGASTUDY"
    allowed_domains = ['megastudy.net']

    start_urls = [
        'http://www.naver.com'
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        start_temp = self.start.split('/')
        till_temp  = self.till.split('/')
        self.start = datetime.date(int(start_temp[0]), int(start_temp[1]), int(start_temp[2]))
        self.till  = datetime.date(int(till_temp[0]), int(till_temp[1]), int(till_temp[2]))

    def parse(self, response):
        print('---- Scraping Starts ----')
        page = 1
        date_qna_dic = defaultdict(int)
        running = True

        while running:
            try:
                co.add_argument(f"user-agent={ua.random}")
                self.browser = webdriver.Chrome(chrome_options = co)
                print(f'Current Page {page}')

                base_url = f'http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=rimbaud666&tec_nm=%uC870%uC815%uC2DD&tec_type=1&brd_cd=784&brd_tbl=MS_BRD_TEC784&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=134&page={str(page)}&chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.24915805251066403'

                self.browser.get(base_url)

                print(f'Online to {base_url}')

                title = WebDriverWait(self.browser, 10) \
                                        .until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table_list > table.commonBoardList > tbody > tr.top")))
                print('table element poped up')

                rows = self.browser.find_elements_by_tag_name('tr')
                rows = rows[4:]

                for row in rows:
                    text = row.text.split()
                    if len(text) > 5:
                        print(f'row_sample: {text}')

                        date_value = text[-2]
                        print(f'date_value: {date_value}')

                        if len(date_value) == 10:

                            # date comparison
                            # if bigger than till, smaller than start, pass
                            date_value = date_value.split('-')

                            # date_value = [2020,12,23]
                            # date_value[0] = 2020 / date_value[1] = 12/ date_value[2] = 23

                            date_value = datetime.date(int(date_value[0]), int(date_value[1]), int(date_value[2]))

                            if date_value <= self.start and date_value >= self.till:
                                date_qna_dic[date_value] += 1
                                print(f'{date_value}=>{date_qna_dic[date_value]}')

                            else:
                                print('out of date-range')
                                running = False
                                break

                page += 1
                print(f'Going to page {page}')

            except Exception as exp:
                print('Error occurred!!')
                print(exp)
                break

        for date in date_qna_dic:
            item = QnaCrawlerItem()
            item['date'] = date
            item['qna_count'] = date_qna_dic[date]
            yield item



class SkySpider(scrapy.Spider):
    name = "SKYEDU"
    allowed_domains = ['skyedu.conects.com']

    start_urls = [
        'http://www.naver.com'
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        start_temp = self.start.split('-')
        till_temp  = self.till.split('-')
        self.start = datetime.date(int(start_temp[0]), int(start_temp[1]), int(start_temp[2]))
        self.till  = datetime.date(int(till_temp[0]), int(till_temp[1]), int(till_temp[2]))

    def parse(self, response):
        print('---- Scraping Starts ----')
        page = 1
        date_qna_dic = defaultdict(int)
        running = True

        while running:
            try:
                co.add_argument(f"user-agent={ua.random}")
                self.browser = webdriver.Chrome(chrome_options = co)

                base_url = f'https://skyedu.conects.com/teachers/teacher_qna/?t_id=jhc01&cat1=1&page={str(page)}'

                self.browser.get(base_url)
                print(f'Online to {base_url}')

                title = WebDriverWait(self.browser, 10) \
                                        .until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.board-list > table")))
                print('table element poped up')

                rows = self.browser.find_elements_by_tag_name('tr')
                rows = rows[4:]

                for row in rows:
                    text = row.text.split()
                    print(f'row_sample: {text}')

                    date_value, writer = text[-1], text[-2]
                    print(f'date_value: {date_value}')
                    print(f'writer: {writer}')

                    if len(date_value) == 10:
                        print(date_value)
                        # date comparison
                        # if bigger than till, smaller than start, pass
                        date_value = date_value.split('-')

                        # date_value = [2020,12,23]
                        # date_value[0] = 2020 / date_value[1] = 12/ date_value[2] = 23

                        date_value = datetime.date(int(date_value[0]), int(date_value[1]), int(date_value[2]))


                        if date_value <= self.start and date_value >= self.till:
                            date_qna_dic[date_value] += 1
                            print(f'{date_value}:{date_qna_dic[date_value]}')

                        else:
                            print('out of date-range')
                            running = False
                            break

                page += 1
                print(f'page {page}')

            except Exception as exp:
                print('Error occurred!!')
                print(exp)
                break

        for date in date_qna_dic:
            item = QnaCrawlerItem()
            item['date'] = date
            item['qna_count'] = date_qna_dic[date]
            yield item

class MiMacSpider(scrapy.Spider):
    name = "MIMAC"
    rotate_user_agent = True

    start_urls = [
              'http://www.naver.com'
                  ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        start_temp = self.start.split('/')
        till_temp  = self.till.split('/')
        self.start = datetime.date(int(start_temp[0]), int(start_temp[1]), int(start_temp[2]))
        self.till  = datetime.date(int(till_temp[0]), int(till_temp[1]), int(till_temp[2]))

    def parse(self, response):
        print('---- Scraping Starts ----')
        page = 1
        date_qna_dic = defaultdict(int)
        running = True

        while running:
            try:
                co.add_argument(f"user-agent={ua.random}")
                self.browser = webdriver.Chrome(chrome_options = co)

                base_url = f'http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=531&currPage={str(page)}'

                self.browser.implicitly_wait(5)
                self.browser.get(base_url)

                print(f'Online to {base_url}')
                # get the rows of table
                rows = self.browser.find_elements_by_tag_name('tr')
                # rows[:3] consists notices
                rows = rows[3:]
                # iterate through rows

                for row in rows:
                    # text is list, consisted by row data
                    text = row.text.split()
                    print(f'row_sample: {text}')
                    if len(text) > 5 :
                        date_value = text[-2]
                        writer = text[-1]
                        if len(date_value) == 10:
                            print(date_value)
                            # date comparison
                            # if bigger than till, smaller than start, pass
                            date_value = date_value.split('/')

                            # date_value = [2020,12,23]
                            # date_value[0] = 2020 / date_value[1] = 12/ date_value[2] = 23

                            date_value = datetime.date(int(date_value[0]), int(date_value[1]), int(date_value[2]))

                            if date_value <= self.start and date_value >= self.till:
                                if writer not in ['운영자', '연구실']:
                                    dic[date_value] += 1
                                    print('got it')

                            else:
                                print('out of date-range')
                                running = False
                                break

                page += 1
                print(f'page {page}')

            except Exception as exp:
                print('Error occurred!!')
                print(exp)
                break
                
        for date in date_qna_dic:
            item = QnaCrawlerItem()
            item['date'] = date
            item['qna_count'] = date_qna_dic[i]
            yield item
