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

def get_proxies(co):
    driver = webdriver.Chrome(chrome_options=co)
    driver.get("https://free-proxy-list.net/")

    PROXIES = []
    proxies = driver.find_elements_by_css_selector("tr[role='row']")
    for p in proxies:
        result = p.text.split(" ")
        if result[-1] == "yes":
            # ㅋㅋㅋㅋㅋ
            # chrome 창이 넓으면 더 많은 column 보임 --> [-1]이 딴놈임
            PROXIES.append(result[0] + ":" + result[1])

    driver.close()
    return PROXIES


# ALL_PROXIES = get_proxies(co)

# refactoring 예시. 마지막 if 문만 다르면, 같은 fn 두번 만들지 말기
def proxied_driver(addresses, driver_type="chrome", co=None):
    assert len(addresses) > 0, "At least one proxy address must be provided"

    prox = Proxy()
    prox.proxy_type = ProxyType.MANUAL
    addr = random.choice(addresses)
    prox.http_proxy = addr
    prox.ssl_proxy = addr

    assert driver_type in ["chrome", "firefox"], "proxy_type must be chrome or firefox "
    if driver_type == "chrome":
        capabilities = webdriver.DesiredCapabilities.CHROME
        prox.add_to_capabilities(capabilities)
        driver = webdriver.Chrome(chrome_options=co, desired_capabilities=capabilities)
        # 참고로 이런 .method의 번거로움이 python 단점 중 하나. 간단한 설정이어야 하는게 이상하게 구성하게됨
    elif driver_type == "firefox":
        capabilities = DesiredCapabilities.FIREFOX
        prox.add_to_capabilities(capabilities)
        driver = webdriver.Firefox(firefox_options=co,
                                   desired_capabilities=capabilities,
                                   executable_path="/usr/local/bin/geckodriver")

    return driver


##########################################################################################################
##########################################################################################################
##########################################################################################################

# 이건 굳이? ㅋㅋ
def parse_date(date_value):
    return parse(date_value)


# 여기 set_foo 라 한게 사실 다 get하는 놈들임.

def set_range(start, till):
    start, till = parse(start).date(), parse(till).date()
    return start, till


def set_range_with_today():
    today = datetime.date.today()
    yesterday = (today - datetime.timedelta(days=1))
    # day_before_yesterday = yesterday - datetime.timedelta(days=1)
    return yesterday, yesterday  # 하나는 today여야하지 않나?

def set_teachers(teacher_name, doc):
    return doc.worksheet(teacher_name)

def mergeDict(dict1, dict2):
    """ Merge dictionaries and keep values of common keys in list"""
    dict3 = {**dict1, **dict2}
    for key, value in dict3.items():
        if key in dict1 and key in dict2:
            dict3[key] = value + dict1[key]

    return dict3

def check_date_range(date, start, till):
    if date <= start and date >= till:
        return 1
    elif date > start:
        # 왜 이 fn 만들고 아래에서 print 반복해서 써...
        print("out of date-range, over {}".format(str(start)))
        return 0
    elif date < till:
        print("out of date-range, less {}".format(str(till)))
        return -1


def row_filter(rows, teacher_name, start, till):
    rows = [
        row.find_elements_by_css_selector("*") for row in rows if
        row.get_attribute("class") in [None, ""]
    ]

    # 자 이게 핵심인데...
    # 미안한데 진짜 토나올뻔 ㅋㅋㅋㅋㅋㅋ
    # 그냥 화면 크게 띄워놓고 희미하게 쳐다볼때 이렇게 반복적이면 뭔가 문제 있는거임
    # 고통정이 뭔지 생각하고 좀빼주자1@#$!@#$

    # site check
    sites = ["etoos", "skyedu", "megastudy", "mimac"]
    curr_site = None
    for site in sites:
        if site in teacher_name:
            curr_site = site
            break
    assert curr_site, "Does teacher belong to {}?".format(sites)

    # date check
    # 이것도 이런식으로 idx로 하기보다 아예 column 명으로 찾는게 table이 조금 바뀌어도 안고장남
    date_idx = {
        "etoos": -1,
        "skyedu": -1,
        "megastudy": -2,
        "mimac": -2
    }
    check_date = lambda row: check_date_range(parse(row[date_idx[curr_site]].date()),
                                              start,
                                              till)

    # filter logic
    questions = [r for r in rows if check_date(r) == 1]
    errors = [r for r in rows if check_date(r) == -1]
    # check_date의 결과값으로 group_by 해서 {"questions": [...], "errors": [...]} 이런식으로 한번에 만들면 가산점 주겠음.

    # special case
    if curr_site == "etoos":
        questions = [q for q in questions if len(q[-2].text) <= 4]

    # 여기서 리턴 값으로 에러 핸들링 하는것도 이상함. 리턴 값과 가동 상태가 이렇게 썪이면 안됨.
    return False if len(errors) > 0 else True, {start: len(list(questions))}

# 더 밑에는 못보겠다. 암튼 이런식으로 계속 ㄱㄱ. 한번도 안돌려본거니 버그 있을텐데 개념을 공부하며 고쳐보던지!

def wait_element(browser, teacher_name):
    if 'etoos' in teacher_name:
        title = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table.subcomm_tbl_board")
                )
            )
    elif 'megastudy' in teacher_name:
        title = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "div.table_list > table.commonBoardList > tbody > tr.top",
                        )
                    )
                )
    elif 'skyedu' in teacher_name:
        title = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.board-list > table")
                    )
                )
    elif 'mimac' in teacher_name:
        title = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.tbltype_list > table")
                    )
                )

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
    #opts.add_argument('--headless')
    print('Firefox Headless Browser Invoked')
    return opts

def find_rows_of_table(browser):
    tbody = browser.find_element_by_tag_name("tbody")
    rows = tbody.find_elements_by_tag_name("tr")
    return rows


class SPIDER_BOARD(scrapy.Spider):
    name = "SPIDERMAN"
    start_urls = ["http://www.naver.com"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Arguments:
        # self.start, self.till, self.teacher
        # if only self.teacher:   set_range_with_today()
        if self.with_range == 'False':
            self.start, self.till = set_range_with_today()

        elif self.with_range == 'True':
            self.start, self.till = set_range(self.start, self.till)

        self.co = driver_setting()
        #self.firefox_setting = driver_setting_firefox()
        self.doc = connect_gspread()
        self.worksheet = set_teachers(self.teacher, self.doc)
        self.teacher_dic = {
            #ETOOS
            "etoos_yhk": "https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200386&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={}",
            "etoos_kww": "https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200245&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={}",
            "etoos_swc": "https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200236&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={}",
            "etoos_grace": "https://www.etoos.com/teacher/board/sub04_math/board_list.asp?teacher_id=200331&selSearchType=&txtSearchWD=&BOARD_ID=2007&QUST_TYPE_CD=&GOOD_QUST_YN=&MOV_YN=&MEM_YN=&NTView=&page={}",

            #MEGASTUDY
            "megastudy_jjs": "http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=rimbaud666&tec_nm=%uC870%uC815%uC2DD&tec_type=1&brd_cd=784&brd_tbl=MS_BRD_TEC784&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=134&page={}&chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.24915805251066403",
            "megastudy_kkh": "http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=megakkh&tec_nm=%uAE40%uAE30%uD6C8&tec_type=1&brd_cd=28&brd_tbl=MS_BRD_TEC28&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=62&page={}&chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.06499842812264811",
            "megastudy_kkc": "http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=kichery&tec_nm=%uAE40%uAE30%uCCA0&tec_type=1&brd_cd=802&brd_tbl=MS_BRD_TEC802&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=145&page={}&chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.9052209945738199",
            "megastudy_jjh": "http://www.megastudy.net/teacher_v2/bbs/bbs_list_ax.asp?tec_cd=megachrisjo21&tec_nm=%uC870%uC815%uD638&tec_type=1&brd_cd=531&brd_tbl=MS_BRD_TEC531&brd_kbn=qnabbs&dom_cd=5&LeftMenuCd=3&LeftSubCd=1&HomeCd=73&page={}&chr_cd=&sub_nm=&ans_yn=&smode=1&sword=&TmpFlg=0.19749594326445652",

            #SKYEDU
            "skyedu_jej": "https://skyedu.conects.com/teachers/teacher_qna/?t_id=jej01&cat1=1&page={}",
            "skyedu_jhc": "https://skyedu.conects.com/teachers/teacher_qna/?t_id=jhc01&cat1=1&page={}",

            #MIMAC
            "mimac_lmh": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=531&currPage={}&myQna=N&ordType=&pageType=home&srchWordType=title&relm=03&type=03531&tcdTabType=tcdHome&menuIdx=&relmName=&tcdName=",
            "mimac_lys": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=926&currPage={}&myQna=N&ordType=&pageType=home&srchWordType=title&relm=03&type=03926&tcdTabType=tcdHome&menuIdx=&relmName=&tcdName=",
            "mimac_esj": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=503&currPage={}&myQna=N&ordType=&pageType=home&srchWordType=title&relm=03&type=03503&tcdTabType=tcdHome&menuIdx=&relmName=&tcdName=",
            "mimac_kjj": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=536&currPage={}&myQna=N&ordType=&pageType=home&srchWordType=title&relm=03&type=03536&tcdTabType=tcdHome&menuIdx=&relmName=&tcdName=",
            "mimac_hjo": "http://www.mimacstudy.com/tcher/studyQna/getStudyQnaList.ds?tcd=922&currPage={}&myQna=N&ordType=&pageType=home&srchWordType=title&relm=03&type=03922&tcdTabType=tcdHome&menuIdx=&relmName=&tcdName="
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
            browser = webdriver.Chrome(chrome_options=self.co)
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


