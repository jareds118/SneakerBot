
# Python SneakerBot - shopnicekicks

Simple automated shoe buying bot for the website www.shopnicekicks.com

Includes functionality for using proxies, waiting in queues, multiple purchase instances, user profiles, out of stock item waiting, etc.

Made for educational purposes only. Not made with the efficiency needed to compete with other bots.

## Authors

- [@jareds118](https://github.com/jareds118)


## Installation

1. Install the project and update the ChromeDriver.exe.
2. Update the project PATH in both 'main.py' and 'mainFunctions.py'.
3. Update the 'config.json' (see below). All information included is for testing only and is not accurate or real.

```bash
  {
  "forBuyModeInput0": 0, // 0 for test mode : 1 for proxy support

  "botIterate": 2, // Total number of bot instances running at once
  "siteName": "shopNiceKicks", // Site name (no support for other websites at this point)
  "url": "https://shopnicekicks.com/products/asics-1201a582-700-gel-lyte-iii-og-mens-lifestyle-shoe-purple", // URL of the shoe to purchase (either available or to be launched)
  "inputSizes": [ "13", "12", "11" ], // Sizes to purchase
  "sleepBetweenSearches": 0.5, // How often to check for stock
  "requestedCheckouts": 1, // Total number of requested successful checkouts

  // Purchaser information
  "fName": "Jared", 
  "lName": "Simon", 
  "city": "Hookstown",
  "country": "United States",
  "state": "Pennsylvania",
  "zip": "15050",

  "gmailArray": [ "steve@gmail.com", "jon@email.vccs.edu", "business@gmail.com" ],
  "adressArray": [ "781 Old Millcreek Road", "781 Old Millcreek Drive", "781 Old Millcreek Rd" ],
  "phoneArray": [ "6125559999", "7245882209", "5619870987" ],
  // Credit card information : Card # | Expiration | CVC
  "cardNumArray": [
    [ "4311233213232233", "1221", "323" ],
    [ "4147423296441056", "1225", "478" ],
    [ "4421512207348916", "1223", "044" ]
  ],

  // Array of proxy addresses to use
  "proxyArray": [
    -1
  ]
}
```
    
