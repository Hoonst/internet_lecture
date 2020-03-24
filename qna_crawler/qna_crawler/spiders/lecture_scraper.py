import scrapy
from scrapy.selector import Selector
from qna_crawler.items import QnaCrawlerItem

from collections import defaultdict
import sys
import datetime
from dateutil.parser import parse
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
from selenium.webdriver.firefox.options import Options

import gspread
from oauth2client.service_account import ServiceAccountCredentials

<<<<<<< HEAD
# scope = [
#     "https://spreadsheets.google.com/feeds",
#     "https://www.googleapis.com/auth/drive",
# ]
#
# json_file_name = "woven-arcadia-269609-12b95dbdd1c3.json"
#
# credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
# gc = gspread.authorize(credentials)
#
# spreadsheet_url = "https://docs.google.com/spreadsheets/d/1YEO-EhcPmtj0r0YJzy-xNF6oVEdb8QHS43Eusck83so/edit#gid=2122150374"
#
# # 스프레스시트 문서 가져오기
# doc = gc.open_by_url(spreadsheet_url)
#
# # 시트 선택하기
#
# ua = UserAgent()
# co = webdriver.ChromeOptions()
# co.add_argument("/Users/yoonhoonsang/Desktop/internet_lecture/qna_crawler/chromedriver")
# co.add_argument("log-level=1")
# co.add_argument("headless")
# co.add_argument("user-agent={}".format(ua.random))
# co.add_argument("lang=ko_KR")

=======
>>>>>>> 9c6426e22acd89e17c189044bd860f4ed9170a97

def get_proxies(co):
    driver = webdriver.Chrome(chrome_options=co)
    driver.get("https://free-proxy-list.net/")

    PROXIES = []
    proxies = driver.find_elements_by_css_selector("tr[role='row']")
    for p in proxies:
        result = p.text.split(" ")
        if result[-1] == "yes":
            PROXIES.append(result[0] + ":" + result[1])

    driver.close()
    return PROXIES


# ALL_PROXIES = get_proxies(co)


def proxy_driver(PROXIES, co):
    prox = Proxy()
    pxy = ""
    if PROXIES:
        pxy = random.choice(PROXIES)  # random proxy
        print(pxy)
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


def proxy_driver_with_firefox(PROXIES, co):
    prox = Proxy()
    pxy = ""
    if PROXIES:
        pxy = random.choice(PROXIES)  # random proxy
        print(pxy)
    else:
        print("--- Proxies used up (%s)" % len(PROXIES))
        PROXIES = get_proxies(co=co)

    prox.proxy_type = ProxyType.MANUAL
    prox.http_proxy = pxy
    prox.ssl_proxy = pxy

    capabilities = DesiredCapabilities.FIREFOX
    prox.add_to_capabilities(capabilities)

    driver = webdriver.Firefox(
        firefox_options=co,
        desired_capabilities=capabilities,
        executable_path="/usr/local/bin/geckodriver",
    )

    return driver


##########################################################################################################
##########################################################################################################
##########################################################################################################


def parse_date(date_value):
    return parse(date_value)


def set_range(start, till):
    start, till = parse(start).date(), parse(till).date()
    return start, till


def set_range_with_today():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    # day_before_yesterday = yesterday - datetime.timedelta(days=1)
    return yesterday, yesterday


def set_teachers(teacher_name, doc):
    return doc.worksheet(teacher_name)


def mergeDict(dict1, dict2):
    """ Merge dictionaries and keep values of common keys in list"""
    dict3 = {**dict1, **dict2}
    for key, value in dict3.items():
        if key in dict1 and key in dict2:
            dict3[key] = value + dict1[key]
<<<<<<< HEAD

    return dict3

=======

    return dict3

>>>>>>> 9c6426e22acd89e17c189044bd860f4ed9170a97

def check_date_range(date, start, till):
    if date <= start and date >= till:
        return 1
    elif date > start:
        return 0
    elif date < till:
        return -1


def row_filter(rows, teacher_name, start, till):
    run = True

    qna_dic = defaultdict(int)

    filtered_notice_rows = [
        row for row in rows if row.get_attribute("class") in [None, ""]
    ]

    # ETOOS
    if "etoos" in teacher_name:
        filtered_rows = []
        for row in filtered_notice_rows:
            td_list = row.find_elements_by_css_selector("*")
            date_value, writer = parse_date(td_list[-1].text).date(), td_list[-2].text
            if len(writer) > 4:
                print("This is not a question, but answer")
                continue
            print("This is a question")
            check = check_date_range(date_value, start, till)
            print("check: ", check)
            if check > 0:
                qna_dic[date_value] += 1
            elif check == 0:
                print("out of date-range, over {}".format(str(start)))
                continue
            elif check < 0:
                print("out of date-range, less {}".format(str(till)))
                run = False
                print("I am broken")
                break

            print("====================")
        return run, qna_dic

    # SKYEDU
    elif "skyedu" in teacher_name:
        for row in filtered_notice_rows:
            td_list = row.find_elements_by_css_selector("*")
            date_value = parse_date(td_list[-1].text).date()

            check = check_date_range(date_value, start, till)
            if check > 0:
                qna_dic[date_value] += 1
            elif check == 0:
                print("out of date-range, over {}".format(str(start)))
                continue
            elif check < 0:
                print("out of date-range, less {}".format(str(till)))
                run = False
                print("I am broken")
                break
        return run, qna_dic

    # MEGASTUDY
    elif "megastudy" in teacher_name:

        for row in filtered_notice_rows:
            td_list = row.find_elements_by_css_selector("*")
            date_value = parse_date(td_list[-2].text).date()

            check = check_date_range(date_value, start, till)
            if check > 0:
                qna_dic[date_value] += 1
            elif check == 0:
                print("out of date-range, over {}".format(str(start)))
                continue
            elif check < 0:
                print("out of date-range, less {}".format(str(till)))
                run = False
                print("I am broken")
                break

        return run, qna_dic

    # MIMAC
    elif "mimac" in teacher_name:
        filtered_rows = []
        for row in filtered_notice_rows:
            td_list = row.find_elements_by_css_selector("*")
            first_td_class = td_list[0].get_attribute("class")

            if first_td_class == "noti":
                continue
            date_value = parse(td_list[-2].text).date()

            check = check_date_range(date_value, start, till)
            if check > 0:
                qna_dic[date_value] += 1
            elif check == 0:
                print("out of date-range, over {}".format(str(start)))
                continue
            elif check < 0:
                print("out of date-range, less {}".format(str(till)))
                run = False
                print("I am broken")
                break

        return run, qna_dic


def wait_element(browser, teacher_name):
    if "etoos" in teacher_name:
        title = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.subcomm_tbl_board"))
        )
    elif "megastudy" in teacher_name:
        title = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.table_list > table.commonBoardList > tbody > tr.top",
                )
            )
        )
    elif "skyedu" in teacher_name:
        title = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.board-list > table"))
        )
    elif "mimac" in teacher_name:
        title = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.tbltype_list > table")
            )
        )
<<<<<<< HEAD


def connect_gspread():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    json_file_name = "woven-arcadia-269609-12b95dbdd1c3.json"

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_file_name, scope
    )
    gc = gspread.authorize(credentials)
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1YEO-EhcPmtj0r0YJzy-xNF6oVEdb8QHS43Eusck83so/edit#gid=2122150374"

    # 스프레스시트 문서 가져오기
    doc = gc.open_by_url(spreadsheet_url)
    return doc


def driver_setting():
    ua = UserAgent()
    co = webdriver.ChromeOptions()
    co.add_argument("/home/yoonhoonsang/internet_lecture/chromedriver")
    co.add_argument("log-level=1")
    co.add_argument("headless")
    co.add_argument("user-agent={}".format(ua.random))
    co.add_argument("lang=ko_KR")
    return co


def driver_setting_firefox():
    opts = Options()
    # opts.add_argument('--headless')
    print("Firefox Headless Browser Invoked")
    return opts


def find_rows_of_table(browser):
    tbody = browser.find_element_by_tag_name("tbody")
    rows = tbody.find_elements_by_tag_name("tr")
    return rows


=======


def connect_gspread():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    json_file_name = "woven-arcadia-269609-12b95dbdd1c3.json"

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_file_name, scope
    )
    gc = gspread.authorize(credentials)
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1YEO-EhcPmtj0r0YJzy-xNF6oVEdb8QHS43Eusck83so/edit#gid=2122150374"

    # 스프레스시트 문서 가져오기
    doc = gc.open_by_url(spreadsheet_url)
    return doc


def driver_setting():
    ua = UserAgent()
    co = webdriver.ChromeOptions()
    co.add_argument('/home/yoonhoonsang/internet_lecture/chromedriver')
    co.add_argument("log-level=1")
    co.add_argument("headless")
    co.add_argument("user-agent={}".format(ua.random))
    co.add_argument("lang=ko_KR")
    return co


def driver_setting_firefox():
    opts = Options()
    # opts.add_argument('--headless')
    print("Firefox Headless Browser Invoked")
    return opts


def find_rows_of_table(browser):
    tbody = browser.find_element_by_tag_name("tbody")
    rows = tbody.find_elements_by_tag_name("tr")
    return rows


>>>>>>> 9c6426e22acd89e17c189044bd860f4ed9170a97
class SPIDER_BOARD(scrapy.Spider):
    name = "SPIDERMAN"
    start_urls = ["http://www.naver.com"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Arguments:
        # self.start, self.till, self.teacher
        # if only self.teacher:   set_range_with_today()
        if self.with_range == "False":
            self.start, self.till = set_range_with_today()

        elif self.with_range == "True":
            self.start, self.till = set_range(self.start, self.till)

        self.co = driver_setting()
        # self.firefox_setting = driver_setting_firefox()
        self.doc = connect_gspread()
        self.worksheet = set_teachers(self.teacher, self.doc)
        self.teacher_dic = {
            # ETOOS
            "etoos_yhk": "https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200386&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={}",
            "etoos_kww": "https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200245&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={}",
            "etoos_swc": "https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200236&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={}",
            "etoos_grace": "https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200331&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={}",
            # MEGASTUDY
            "megastudy_jjs": "http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=rimbaud666&tec_nm=%uC870%uC815%uC2DD&tec_type=1&brd_cd=784&brd_tbl=MS_BRD_TEC784&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=134&page={}&chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.24915805251066403",
            "megastudy_kkh": "http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=megakkh&tec_nm=%uAE40%uAE30%uD6C8&tec_type=1&brd_cd=28&brd_tbl=MS_BRD_TEC28&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=62&page={}&chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.06499842812264811",
            "megastudy_kkc": "http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=kichery&tec_nm=%uAE40%uAE30%uCCA0&tec_type=1&brd_cd=802&brd_tbl=MS_BRD_TEC802&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=145&page={}&chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.9052209945738199",
            "megastudy_jjh": "http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=megachrisjo21&tec_nm=%uC870%uC815%uD638&tec_type=1&brd_cd=531&brd_tbl=MS_BRD_TEC531&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=73&page={}&chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.19749594326445652",
            # SKYEDU
            "skyedu_jej": "https://skyedu.conects.com/teachers/teacher_qna/?t_id=jej01&cat1=1&page={}",
            "skyedu_jhc": "https://skyedu.conects.com/teachers/teacher_qna/?t_id=jhc01&cat1=1&page={}",
            # MIMAC
            "mimac_lmh": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=531&currPage={}&myQna=N&ordType=&pageType=home&srchWordType=title&relm=03&type=03531&tcdTabType=tcdHome&menuIdx=&relmName=&tcdName=",
            "mimac_lys": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=926&currPage={}&myQna=N&ordType=&pageType=home&srchWordType=title&relm=03&type=03926&tcdTabType=tcdHome&menuIdx=&relmName=&tcdName=",
            "mimac_esj": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=503&currPage={}&myQna=N&ordType=&pageType=home&srchWordType=title&relm=03&type=03503&tcdTabType=tcdHome&menuIdx=&relmName=&tcdName=",
            "mimac_kjj": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=536&currPage={}&myQna=N&ordType=&pageType=home&srchWordType=title&relm=03&type=03536&tcdTabType=tcdHome&menuIdx=&relmName=&tcdName=",
            "mimac_hjo": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=922&currPage={}&myQna=N&ordType=&pageType=home&srchWordType=title&relm=03&type=03922&tcdTabType=tcdHome&menuIdx=&relmName=&tcdName=",
        }

    def parse(self, response):
        print(vars(self))
        print("---- Scraping Starts ----")
        print("---- Scraping of {}".format(str(self.start)))

        page, qna_dictionary, running = 1, defaultdict(int), True
        print(driver_setting())
        while running:
            #             if 'mimac' in self.teacher:
            #                 browser = proxy_driver_with_firefox(ALL_PROXIES, self.firefox_setting)
            #             else:
<<<<<<< HEAD
            browser = webdriver.Chrome(chrome_options=self.co)
=======
            browser = webdriver.Chrome(chrome_options=self.co, executable_path='/home/yoonhoonsang/internet_lecture/chromedriver')
>>>>>>> 9c6426e22acd89e17c189044bd860f4ed9170a97
            print("Current Page {}".format(page))
            base_url = self.teacher_dic[self.teacher].format(str(page))
            browser.get(base_url)

            print("Accessing {}".format(base_url))
            wait_element(browser, self.teacher)
            print("table element poped up")

            rows = find_rows_of_table(browser)
            running, qna_dic = row_filter(rows, self.teacher, self.start, self.till)
            qna_dictionary = mergeDict(qna_dictionary, qna_dic)

            if running == False:
                break
            page += 1

        for date in qna_dictionary:
            print("Final Process...")
            self.worksheet.append_row([str(date), str(qna_dictionary[date])])

            item = QnaCrawlerItem()
            item["date"] = date
            item["qna_count"] = qna_dictionary[date]

            yield item
