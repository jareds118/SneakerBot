import shopNiceKicks

import json
import requests
import bs4
import random
import webbrowser
import lxml
import time
import random
import queue

import multiprocessing
from multiprocessing import Process, Queue

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

import colorama
from colorama import init
from colorama import Fore
init()

#import configs
with open('D:\PythonBot\configs\config.json') as jsonFile:
    data = json.load(jsonFile)

#set variables from config
site = shopNiceKicks #this needs to be modular in the future
path = "D:\PythonBot\ChromeDriver\chromedriver.exe"
url = data['url']
inputSizes = data['inputSizes']
botIterate = data['botIterate']
firstName = data['fName']
lastName = data['lName']
city = data['city']
country = data['country']
state = data['state']
zip = data['zip']
proxyConfig = data['proxyArray']
testMode = data['forBuyModeInput0']
if testMode == 0:
    testMode = True
else:
    testMode = False

def preDropInformation(url,proxyData):
    #find all sizes on page
    if testMode:
        sizes = site.findAllSizes(url,-1)
    else:
        proxyData = "http://" + proxyData
        proxies = {
          'https': proxyData,
        }
        sizes = site.findAllSizes(url,proxies)
    #confirm sizes requested exists
    wantedSizes = []
    for i in sizes[0]:
        if i in inputSizes:
            wantedSizes.append(i)

    #find url for all sizes
    allSizeVariables = site.findSizeVariable(url)
    allSizeUrl = []

    for i in sizes[0]:
        index = sizes[0].index(i)
        uniqueUrl = site.createUniqueUrl(url, allSizeVariables, index)
        allSizeUrl.append(uniqueUrl)
    return (allSizeUrl, sizes[0])
preDropInfo = preDropInformation(url,proxyConfig[0])
#make sure return is not non
if preDropInfo is None:
    print (Fore.RED + 'CRITICAL ERROR: preDropInfo returned as None. Restart program!')
sizeUrlArray = preDropInfo[0]

def addToCartUrl(url,proxyData):
    #check what items are in stock
    if not proxyData == -1:
        proxyData = "http://" + proxyData
        proxies = {
          'https': proxyData,
        }
        stock = site.findAllSizes(url,proxies)
    else:
        stock = site.findAllSizes(url,-1)

    if stock[1] == []:
        return 0

    #find size requested that's in stock
    inStockSize = 0
    for i in inputSizes:
        if i in stock[1]:
            inStockSize = i
            break
    if inStockSize == 0:
        print (Fore.BLUE + 'SOLD OUT  - addToCartHC: All requested sizes are not in stock')
        return 0

    #pick size url that is in stock
    index = stock[0].index(inStockSize)
    uniqueUrl = sizeUrlArray[index]

    return uniqueUrl

def captchaSolver(url,proxyData):
    #proxy settings
    if not proxyData == -1:
        #make captcha use proxy too
        proxy = proxyData # IP:PORT or HOST:PORT
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % proxy)

        driver = webdriver.Chrome(path,options=chrome_options)
    else:
        driver = webdriver.Chrome(path)

    driver = webdriver.Chrome(path)
    #strip url
    sub = '.com'
    cutUrl = url[:url.index(sub) + len(sub)]
    uniqueUrl = cutUrl + '/checkpoint'
    driver.get(uniqueUrl)

    icon = driver.find_element("xpath", '//*[(@id = "g-recaptcha-response")]')
    #make display visable by removing 'display = nothing' with java script
    driver.execute_script("arguments[0].style.display = ''; arguments[0].style.padding = '10px';", icon)
    #focus on the element as it is not clickable with java script
    driver.execute_script("arguments[0].focus();", icon)

    #waitUntil captcha solved
    while ((icon.get_attribute('value')) == ''):
        driver.execute_script("arguments[0].focus();", icon)
        time.sleep(1)

    r = icon.get_attribute('value')

    #exitDriver
    driver.quit()

    return (r)

def headlessClientPurchaseSequence(q,url,proxyData,infoArray,botNum):
    #get cart url
    uniqueUrl = addToCartUrl(url,proxyData)

    #proxy settings
    if not proxyData == -1:
        #make captcha use proxy too
        proxy = proxyData # IP:PORT or HOST:PORT
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % proxy)

        driver = webdriver.Chrome(path,options=chrome_options)
    else:
        driver = webdriver.Chrome(path)

    #selenium
    driver.get(uniqueUrl)

    #set info from infoArray
    gmailArray = infoArray[0]
    adressArray = infoArray[1]
    phoneArray = infoArray[2]
    cardNumArray = infoArray[3]

    #click purchase button and wait for load ---------------------------------------------------------------------------
    driver.find_element("xpath", '//*[contains(concat( " ", @class, " " ), concat( " ", "Button--full", " " ))]').click()

    #check redirect, if in queue or checkpoint move on, if sent to home screen exit
    rPage = driver.current_url
    if not (rPage.find('queue')) == -1:
        print (Fore.YELLOW + botNum + 'PAUSE - Bot detected throttle queue')
    else:
        if (rPage.find('checkouts')) == -1 and (rPage.find('checkpoint')) == -1:
            driver.quit()
            print (Fore.RED + botNum + 'FAIL - headlessClient: Bot redirected from checkout page')
            return

    #wait until out of queue if in queue
    while not (driver.current_url.find('queue')) == -1:
        time.sleep(1)

    #check for captcha
    if not (driver.current_url.find('checkpoint')) == -1:
        print (Fore.YELLOW + botNum + 'Captcha detected - manually solving necassary')
        #prepare captcha fill field
        icon = driver.find_element("xpath", '//*[(@id = "g-recaptcha-response")]')
        #make display visable by removing 'display = nothing' with java script
        driver.execute_script("arguments[0].style.display = ''; arguments[0].style.padding = '10px';", icon)
        #focus on the element as it is not clickable with java script
        driver.execute_script("arguments[0].focus();", icon)

        #wait for manual captcha solve
        r = captchaSolver(url,proxyData)
        #send key
        icon.send_keys(r)
        #click submit
        driver.find_element("xpath", '//*[contains(concat( " ", @class, " " ), concat( " ", "btn", " " ))]').click()

    #wait until out of queue if in queue
    while not (driver.current_url.find('queue')) == -1:
        time.sleep(1)

    try:
        element = WebDriverWait(driver, 10).until(
            #in the future this needs to be modular - purchase button
            EC.element_to_be_clickable((By.XPATH, '//*[(@id = "continue_button")]'))
        )
    except:
        driver.quit()
        print (Fore.RED + botNum + 'FAIL - headlessClient: Checkout redirect error : Unknown')
        return

    print (Fore.YELLOW + botNum + 'Sucessfully through throttle queue')

    #uncheck the "Keep me up to date on news and exclusive offers" ---------------------------------------------------------------------------
    driver.find_element("xpath", '//*[(@id = "checkout_buyer_accepts_marketing")]').click()

    #start filling in checkout information
    driver.find_element("xpath", '//*[(@id = "checkout_email")]').send_keys(gmailArray)

    driver.find_element("xpath", '//*[(@id = "checkout_shipping_address_first_name")]').send_keys(firstName)

    driver.find_element("xpath", '//*[(@id = "checkout_shipping_address_last_name")]').send_keys(lastName)

    driver.find_element("xpath", '//*[(@id = "checkout_shipping_address_address1")]').send_keys(adressArray)

    #driver.find_element_by_xpath('//*[(@id = "checkout_shipping_address_address2")]').send_keys("")

    driver.find_element("xpath", '//*[(@id = "checkout_shipping_address_city")]').send_keys(city)

    driver.find_element("xpath", '//*[(@id = "checkout_shipping_address_zip")]').send_keys(zip)

    driver.find_element("xpath", '//*[(@id = "checkout_shipping_address_phone")]').send_keys(phoneArray)

    #select dropdown for state
    stateDropdown = driver.find_element("xpath", '//*[(@id = "checkout_shipping_address_province")]')
    sel = Select(stateDropdown)
    sel.select_by_visible_text(state)

    #select dropdown for country
    countryDropdown = driver.find_element("xpath", '//*[(@id = "checkout_shipping_address_country")]')
    sel = Select(countryDropdown)
    sel.select_by_visible_text(country)

    #check the agree to terms and conditions
    driver.find_element("xpath", '//*[(@id = "i-agree__checkbox")]').click()

    #click continue to shipping
    driver.find_element("xpath", '//*[(@id = "continue_button")]').click()

    try:
        element = WebDriverWait(driver, 10).until(
            #in the future this needs to be modular - purchase button
            EC.element_to_be_clickable((By.XPATH, '//*[(@id = "btn-edit-address")]'))
        )
    except:
        driver.quit()
        print (Fore.RED + botNum + 'FAIL - headlessClient: Address adjustment screen failed to load || address not accepted as legitamite')
        return

    #click keep inputted adress - go to shipping screen ---------------------------------------------------------------------------
    driver.find_element("xpath", '//*[(@id = "originalAddress")]//button').click()

    try:
        element = WebDriverWait(driver, 10).until(
            #in the future this needs to be modular - purchase button
            EC.element_to_be_clickable((By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "section--shipping-method", " " ))]'))
        )
    except:
        driver.quit()
        print (Fore.RED + botNum + ' FAIL - headlessClient: Failed to go to shipping screen')
        return

    #click continue to payment on shipping screen ---------------------------------------------------------------------------
    driver.find_element("xpath", '//*[(@id = "continue_button")]').click()

    try:
        element = WebDriverWait(driver, 10).until(
            #in the future this needs to be modular - purchase button
            EC.element_to_be_clickable((By.XPATH, '//*[(@id = "continue_button")]'))
        )
    except:
        driver.quit()
        print (Fore.RED + botNum + 'FAIL - headlessClient: Failed to click out of shipping screen')
        return

    #payment information screen ---------------------------------------------------------------------------
    cNum = cardNumArray[0]
    cNumber = driver.find_element("xpath", '//*[contains(concat( " ", @class, " " ), concat( " ", "card-fields-iframe", " " ))]')
    cNumber.send_keys(cNum[:4])
    cNumber.send_keys(cNum[4:8])
    cNumber.send_keys(cNum[8:12])
    cNumber.send_keys(cNum[12:16])

    cfvNum = cardNumArray[2]
    driver.find_element("xpath", '//*[contains(@id, "card-fields-verification_value-")]').send_keys(cfvNum)

    #dynamic changing xpaths
    driver.find_element("xpath", '//*[contains(@id, "card-fields-name-")]').send_keys(firstName + " " + lastName)

    expNum = cardNumArray[1]
    cExpiration = driver.find_element("xpath", '//*[contains(@id, "card-fields-expiry-")]')
    cExpiration.send_keys(expNum[:2])
    cExpiration.send_keys(expNum[2:4])

    #complete payment  ---------------------------------------------------------------------------
    if testMode:
        driver.find_element("xpath", '//*[(@id = "continue_button")]').click()
    else:
        driver.quit()
        print (Fore.YELLOW + botNum + 'EXIT: Purchase mode disabled. Bot cancelled before purchasing items.')
        return

    #check for captcha
    if not (driver.current_url.find('checkpoint')) == -1:
        print (Fore.YELLOW + botNum + 'Captcha detected - manually solving necassary')
        #prepare captcha fill field
        icon = driver.find_element("xpath", '//*[(@id = "g-recaptcha-response")]')
        #make display visable by removing 'display = nothing' with java script
        driver.execute_script("arguments[0].style.display = ''; arguments[0].style.padding = '10px';", icon)
        #focus on the element as it is not clickable with java script
        driver.execute_script("arguments[0].focus();", icon)

        #wait for manual captcha solve
        r = captchaSolver(url)
        #send key
        icon.send_keys(r)
        #click submit
        driver.find_element("xpath", '//*[contains(concat( " ", @class, " " ), concat( " ", "btn", " " ))]').click()

    #check to see if payment is successful
    try:
        element = WebDriverWait(driver, 10).until(
            #in the future this needs to be modular - purchase button
            EC.element_to_be_clickable((By.XPATH, '//*[(@id = "continue_button")]'))
        )
    except:
        driver.quit()
        print (Fore.GREEN + 'CHECKOUT - Checkout Sucessful/Stuck in payment loop')
        totalCheckouts += 1
        #put infoArray in Queue for other file to remove from possible information
        q.put(infoArray)
    print (Fore.RED + botNum + 'FAIL - headlessClient: Payment information declined')
