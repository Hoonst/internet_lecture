from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import os
from pathlib import Path


def set_driver():
    global driver, actionChains
    driver = webdriver.Chrome()
    actionChains = ActionChains(driver)
    
def click_be_by_class(element):
    driver.find_element_by_css_selector(element).click()

def connect_site_with_url(site_url, timing):
    driver.get(site_url)
    implicit_wait(timing)
    
def username_password_insert(username, password):
    user = driver.find_element_by_name("userid")
    pw = driver.find_element_by_name("password")
    user.send_keys(username)
    pw.send_keys(password)

    driver.find_element_by_class_name("submit").click()
    
def implicit_wait(timing):
    driver.implicitly_wait(timing)

def scroll_very_bottom(very_bottom_element, timing):
    driver.execute_script('arguments[0].scrollIntoView(true);', very_bottom_element)
    implicit_wait(timing)
    
def actual_performance(plausible_name):
    driver.get(division_dic['division_1'])
    implicit_wait(5)
    try:
        to_element = driver.find_element_by_css_selector("upload-modal.ng-scope")
        scroll_very_bottom(to_element, 5)
        implicit_wait(5)

        if driver.find_elements_by_xpath(f"//*[contains(text(), '{plausible_name}')]") != []:
#           print(driver.find_elements_by_xpath(f"//*[contains(text(), '{plausible_name}')]"))
            actionChains = ActionChains(driver)
            button = driver.find_elements_by_xpath(f"//*[contains(text(), '{plausible_name}')]")[0]
            actionChains.move_to_element(button).context_click(button).perform()

            implicit_wait(5)

            content = driver.find_element_by_css_selector('td.link > a.ng-binding')
            text = content.text
            
            #Some-how updating cell function's index doesn't start from 0
            #test_sheet.update_cell(row, 12, text)
            
    except Exception as e:
        print(e)
        
def download_image_with_url(url, name):   
    os.system(f'wget --output-document={name}{Path(url).suffix} {url}')
    
def determine_s3_component(url):
    logo_url_prefix_ver1 = 'https://s3.amazonaws.com/footballpedia/logo/'
    logo_url_prefix_ver2 = 'https://footballpedia.s3.amazonaws.com/logo/'
    if (logo_url_prefix_ver1 in url) or (logo_url_prefix_ver2 in url):
        return True
    else:
        return False

def driver_enter():
    html = driver.find_element_by_css_selector("body")
    html.send_keys(Keys.RETURN)

def say_yes_to_alert():
    alert = driver.switch_to.alert
    alert.accept()

def say_no_to_alert():
    alert = driver.switch_to.alert
    alert.dismiss()

def maximize_window():
    driver.maximize_window()

def refresh_window():
    driver.refresh()
