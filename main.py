import mainFunctions
import shopNiceKicks

import random
import time
import json

from os import system

import multiprocessing
from multiprocessing import Process, Queue

import colorama
from colorama import init
from colorama import Fore
init()

#import configs
with open('D:\PythonBot\configs\config.json') as jsonFile:
    data = json.load(jsonFile)

#set variables from config
url = data['url']
requestedCheckouts = data['requestedCheckouts']
botIterate = data['botIterate']
sleepRange = data['sleepBetweenSearches']
gmailArray = data['gmailArray']
adressArray = data['adressArray']
phoneArray = data['phoneArray']
cardNumArray = data['cardNumArray']
proxyData = data['proxyArray']
testMode = data['forBuyModeInput0']

if __name__ == '__main__':
    if testMode == 0:
        print (Fore.YELLOW + "---" + Fore.RED + 'PURCHASE MODE ENABLED: ' + "BOT WILL ACTUALLY MAKE PURCHASES" + Fore.YELLOW + "---")
        print (Fore.WHITE + "Enter (continue) to proceed: ")
        x = input()
        if not x == "continue":
            while True:
                print (Fore.RED + "PAUSING: User did not want to continue in purchase mode")
                time.sleep(15)
    else:
        #test mode
        proxyData = -1
        print ("Test Mode Enabled")

def main(url):
    global botIterate
    jobs = []
    q = Queue()
    c = 0
    proxyCounter = 0
    if not proxyData == -1:
        totalProxies = len(proxyData) - 1
    else:
        proxy = -1
    totalCheckouts = 0
    #toDo system to make sure all proxies work

    while True:
        #check to see if totalCheckouts hits requested amount
        if (requestedCheckouts <= totalCheckouts):
            print (Fore.GREEN + 'COMPLETE: Total requested checkouts met')
            return

        #deal with the information in the Queue so we don't get re-checkouts
        if q.empty() == False:
            for i in range(q.qsize()):
                #delete items in Queue from possible information
                rArray = q.get()
                gmailArray.remove(rArray[0])
                adressArray.remove(rArray[1])
                phoneArray.remove(rArray[2])
                cardNumArray.remove(rArray[3])
                #add to counter
                totalCheckouts += 1

        #delete failed and completed jobs
        jobs = [job for job in jobs if job.is_alive()]
        #check to see if there is room for more bots
        if len(jobs) < botIterate:
            #make sure proxy counter doesn't go past the amount of elemts && pick next proxy
            if not proxyData == -1:
                if proxyCounter > (len(proxyData) - 1):
                    proxyCounter = 0
                proxy = proxyData[proxyCounter]

            #check to see if in stock currently
            r = mainFunctions.addToCartUrl(url,proxy)
            if not isinstance(r, str):
                print (Fore.BLUE + 'PAUSE - main: WAITING ON STOCK')
            else:
                #find shortest length of all the arrays
                lenArray = min([len(gmailArray),len(adressArray),len(phoneArray),len(cardNumArray)])

                #if no information left in one of the arrays, exit
                if lenArray == 0:
                    print (Fore.GREEN + 'COMPLETE: Bot used all possible information')
                    return

                for i in range(botIterate - len(jobs)):
                    #check to see if there is NOT enough information left for an extra job
                    if (lenArray <= i):
                        break
                    #check to see if counter is higher than amount in smallest array of info
                    if (c >= lenArray):
                        c = 0
                        botIterate = lenArray
                        break
                    #make sure proxy counter doesn't go past the amount of elemts && pick next proxy
                    if not proxyData == -1:
                        if proxyCounter > (len(proxyData) - 1):
                            proxyCounter = 0
                        proxy = proxyData[proxyCounter]

                    #select info to send to job and send job
                    p = multiprocessing.Process(target=mainFunctions.headlessClientPurchaseSequence,args=[q,url,proxy,[gmailArray[c],adressArray[c],phoneArray[c],cardNumArray[c]],('Bot ' + str(i)) + ' - '])
                    jobs.append(p)
                    p.start()

                    #counters
                    c += 1
                    proxyCounter += 1

        #update CMD title
        system("title " + ("Sneaker Bot (Beta) - Checkouts: " + str(totalCheckouts)))

        #sleep random time from config - randomize slightly
        time.sleep(sleepRange + (random.random() / 2))

if __name__ == '__main__':
    main(url)
