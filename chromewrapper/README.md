# ChromeWrapper

This is a simple wrapper around Selenium and a headless chrome/chromium instance that i threw together for automating mass collection of website screenshots. It also comes with a simple REST API via Flask.

Requirements:

 - Linux (written/tested on ubuntu 16.04, other distros = YMMV)
 - chrome or chromium-browser
 - chromedriver
 - python 3

Virtualenv/pip is also recommended for portability.

on ubuntu, you can run the following apt-get command to install required packages:

`sudo apt install chromium-browser chromium-chromedriver libpython3-dev virtualenv`

Python libraries used:
 - Selenium
 - psutil
 - Flask (for REST API)
 - validators (for REST API)
 - requests (for REST API client)

use `pip install -r requirements.txt` to install the requirements.


## What works so far:

 - retrieving URL screenshots
 - retrieving URL source code
 - Basic URL validation

## Todo:

 - Pooled/persistent chromewrapper instances for the REST API
 - logging
 - more error checking!
 - even more error checking!
 - tests!
 - proper tests!
