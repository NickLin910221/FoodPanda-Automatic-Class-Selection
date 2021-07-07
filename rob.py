#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import re
import time

import loguru
import requests
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

data, select = [], []

start, end = "", ""

### Open the browser
browser = webdriver.Chrome()
browser.minimize_window()
browser.get('https://tw.usehurrier.com/app/rooster/web/login')
# wait fot the website response
browser.implicitly_wait(2)

### LOGIN
print("請輸入您的熊貓帳號")
username = input()
print("請輸入您的熊貓密碼")
pw = input()
print("請輸入您想選擇的時段開始時間 EX: HH:MM")
start = input()
print("請輸入您想選擇的時段結束時間 EX: HH:MM")
end = input()
username_ = browser.find_element_by_xpath("/html/body/div/div[3]/form/div/div[1]/input")
pw_ = browser.find_element_by_xpath("/html/body/div/div[3]/form/div/div[2]/input")
username_.send_keys(username)
pw_.send_keys(pw)
pw_.submit()
# wait fot the website response
time.sleep(5)

browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/div').click()
browser.implicitly_wait(1)
print("Please Press Enter to process filter")
input()

browser.find_element_by_xpath("/html/body/div[2]/div/div/div/div[3]/div[12]").click()
browser.implicitly_wait(1)
browser.find_element_by_xpath("/html/body/div[2]/div/div/div/div[3]/div[13]").click()
browser.implicitly_wait(1)
browser.find_element_by_xpath('/html/body/div[2]/div/div/div/div[4]/div/div[2]/button').click()
browser.implicitly_wait(1)

### Filter
def filt():
    global data,my_time_period_count_sum,select
    data = []
    select = []
    try:
        my_time_period_count = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[3]/div/div[1]/span').text
        my_time_period_count_sum = my_time_period_count.strip("My Shifts ()")
        print("There are " + my_time_period_count_sum + " My shifts")
    except selenium.common.exceptions.NoSuchElementException as error:
        if str(error)[:50] == "Message: no such element: Unable to locate element":
            my_time_period_count_sum = 0
            print("No Shifts available for this day")
            pass

    try:
        time_period_count = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[3]/div/div[2]/span').text
        time_period_count_sum = time_period_count.strip("Available Shifts ()")
        if time_period_count_sum == "No Shifts available for this day":
            time_period_count_sum = 0
    except selenium.common.exceptions.NoSuchElementException as error:
        loguru.logger.debug(error)
        time_period_count_sum = 0
        print("There aren't shifts available for this day")
        pass

    if int(my_time_period_count_sum) == 0 and int(time_period_count_sum) != 0:  ### There is no time period in today
        for i in range(int(time_period_count_sum)):
            try:
                timename = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[3]/div/div[' + str(i+3) + ']/div[1]/p').text
                timezone = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[3]/div/div[' + str(i+3) + ']/div[1]/small').text
            except selenium.common.exceptions.NoSuchElementException:
                continue
            if "北高雄" in timename:
                a = re.split("–|/| ",timezone)
                if len(a) >7:
                    data.append({"id":str(i+3),"timename":timename,"timestart":a[0],"timeend":a[3],"timeperiod":str(a[6]+a[7])})
                else:
                    data.append({"id":str(i+3),"timename":timename,"timestart":a[0],"timeend":a[3],"timeperiod":a[6]})    
            else:
                pass
    
    if int(my_time_period_count_sum) != 0 and int(time_period_count_sum) != 0:  ### There are time periods in today
        for i in range(int(time_period_count_sum)):
            try:
                timename = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[3]/div/div[' + str(i+4) + ']/div[1]/p').text
                timezone = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[3]/div/div[' + str(i+4) + ']/div[1]/small').text
            except selenium.common.exceptions.NoSuchElementException as error:
                loguru.logger.debug(error)
                print(error)
                continue
            if "北高雄" in timename:
                a = re.split("–|/| ",timezone)
                if len(a) >7:
                    data.append({"id":str(i+3),"timename":timename,"timestart":a[0],"timeend":a[3],"timeperiod":str(a[6]+a[7])})
                else:
                    data.append({"id":str(i+3),"timename":timename,"timestart":a[0],"timeend":a[3],"timeperiod":a[6]})  
            else:
                pass
    
    if int(my_time_period_count_sum) != 0 and int(time_period_count_sum) == 0:
        pass
    
    if len(data) != 0:
        print(json.dumps(data,indent=4))
    else:
        pass

def choose():
    global select
    if len(select) > 0:
        for x in range(len(select)):
            print("PICKUP  ",data[int(select[x])])
            ID = data[int(select[x])]["id"]
            try:
                shift_name = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[3]/div/div[' + str(ID) + ']/div[1]/p').text
                shift_period = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[3]/div/div[' + str(ID) + ']/div[1]/small').text
                if str(shift_name) == data[int(select[x])]["timename"] and str(shift_period) == str(data[int(select[x])]["timestart"]) + " – " + str(data[int(select[x])]["timeend"]) + " / " + str(data[int(select[x])]["timeperiod"]):
                    browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[3]/div/div[' + str(int(ID)-x) + ']/div[2]/button').click()
                    browser.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/button[2]').click()
                    browser.implicitly_wait(1)
                else:
                    pass
            except selenium.common.exceptions.ElementClickInterceptedException as error:
                loguru.logger.debug(error)
                print(error)
                pass
            except selenium.common.exceptions.NoSuchElementException as error:
                loguru.logger.debug(error)
                print(error)
                continue
            
            try:
                browser.find_element_by_xpath('/html/body/div[3]/div/div/div/div[3]/button[1]').click()
            except selenium.common.exceptions.NoSuchElementException as error:
                loguru.logger.debug(error)
                print("Take shift Success! Don't need to cancel")
                pass
    if len(select) == 0:
        print("There aren't suitable Shifts for this day")
    
def algo(start,end,repeat):
    
    if repeat == True:
        filt()
    if repeat == False:
        pass
    
    for i in range(len(data)):
        if int(str(data[i]["timestart"])[:2]) <= int(str(start)[:2]):
            continue
        if int(str(data[i]["timestart"])[:2]) == int(str(start)[:2]) and int(str(data[i]["timestart"])[3:]) < int(str(start)[3:]):
            print(int(str(data[i]["timestart"])[:2]),int(str(start)[:2]),int(str(data[i]["timestart"])[3:]),int(str(start)[3:]))
            select.append(str(i))
            print("1")
            return algo(str(data[i]["timeend"]),end,repeat=False)
        if int(str(data[i]["timestart"])[:2]) == int(str(start)[:2]) and int(str(data[i]["timestart"])[3:]) == int(str(start)[3:]):
            print(int(str(data[i]["timestart"])[:2]),int(str(start)[:2]),int(str(data[i]["timestart"])[3:]),int(str(start)[3:]))
            select.append(str(i))
            print("2")
            return algo(data[i]["timeend"],end,repeat=False)        
        if int(str(data[i]["timestart"])[:2]) == int(str(start)[:2]) and int(str(data[i]["timestart"])[3:]) > int(str(start)[3:]):
            continue
        if int(str(data[i]["timestart"])[:2]) >= int(str(start)[:2]) and int(str(data[i]["timeend"])[4:]) <= int(str(end)[4:]) and int(str(data[i]["timeend"])[:2]) <= int(str(end)[:2]):
            print(int(str(data[i]["timestart"])[:2]),int(str(start)[:2]))
            select.append(str(i))
            print("3")
            return algo(str(data[i]["timeend"]),end,repeat=False)
        if data[i]["timestart"] == start and int(str(start)[:2]) <= int(str(end)[:2]) and int(str(start)[3:]) <= int(str(end)[3:]):
            print(int(str(data[i]["timestart"])[:2]),int(str(start)[:2]),int(str(data[i]["timestart"])[3:]),int(str(start)[3:]))
            select.append(str(i))
            print("4")
            return algo(data[i]["timeend"],end,repeat=False)
        if int(str(start)[:2]) > int(str(end)[:2]):
            choose()
        if int(str(start)[:2]) == int(str(end)[:2]) and int(str(start)[3:]) >= int(str(end)[3:]):
            choose()
    choose()

def date(date):
    try:
        browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/div/div[' + str(date) + ']/span[2]').click()
        time.sleep(5)
        m = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/p').text
        d = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/div/div[' + str(date) + ']/span[2]').text
        print(str(d) + "\a  " + str(m))
        return algo(start,end,repeat=True)
    except selenium.common.exceptions.StaleElementReferenceException as error:
        loguru.logger.debug(error)
        print(error)
        return algo(start,end,repeat=True)
    except selenium.common.exceptions.ElementClickInterceptedException as error:
        loguru.logger.debug(error)
        print(error)
        return algo(start,end,repeat=True)

while True:
    for day in range(7):
        date(day+1)
    browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/div/div[11]/span[2]').click()
    time.sleep(2)
    for day in range(7):
        date(day+8)