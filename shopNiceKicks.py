
import requests
import bs4
import random
import webbrowser
import lxml
import fake_useragent
from fake_useragent import UserAgent

#ToDo randomize headers
def findAllSizes(url,proxy):
    #random header
    ua = UserAgent()
    headers = {'User-Agent':str(ua.chrome)}

    #check if proxy is included or -1 (For testing)
    if (proxy == -1):
        rawHtml = requests.get(url, headers=headers)
    else:
        rawHtml = requests.get(url, headers=headers, proxies=proxy)

    page = bs4.BeautifulSoup(rawHtml.text, "lxml")
    #Use inspector gadget to find this part - whole list box
    sizeButtons = page.select('#shopify-section-product-template .HorizontalList__Item')

    #select each index and find value to add to array
    sizeAr = []
    inStock = []
    for i in sizeButtons:
        value = i.input['value']
        sizeAr.append(value)
        #append if size available
        soldOut = i.label['class']
        if not 'gb-change-color' in soldOut:
            inStock.append(value)
    return (sizeAr,inStock)

def findSizeVariable(url):
    #random header
    ua = UserAgent()
    headers = {'User-Agent':str(ua.chrome)}

    rawHtml = requests.get(url, headers=headers)
    page = bs4.BeautifulSoup(rawHtml.text, "lxml")

    #find the size id's through page content
    productList = page.select('.Select--primary')

    #make an array of each size variable
    sizeVariables = []
    for i in productList[0].findAll('option'):
        sizeVariables.append(i['value'])
    return (sizeVariables)

def createUniqueUrl(url, sizeVariables, sIndex):
    #Remove string after .com
    sub = '.com'
    cutUrl = url[:url.index(sub) + len(sub)]
    #Join new string
    uniqueUrl = cutUrl + '/cart/add?id=' + str(sizeVariables[sIndex]) + '&quantity=1'
    return (uniqueUrl)

def checkoutUrl(url):
    #Remove string after .com
    sub = '.com'
    cutUrl = url[:url.index(sub) + len(sub)]
    #Join new string
    uniqueUrl = cutUrl + '/checkout'
    return uniqueUrl
