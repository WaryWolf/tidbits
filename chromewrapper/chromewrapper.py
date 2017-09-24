#/usr/bin/env python

# stdlib imports
import re
import os
from time import strftime, gmtime
import logging
import subprocess
import signal
import shutil
import random

# 3rd party imports
#import psutil
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


class ChromeWrapper():

    _driver = None
    _driverpid = None

    def __init__(self, options=None, chrome_binary=None, chromedriver_binary=None):
    
        if options == None:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--mute-audio')    # can really freak you out otherwise
            options.add_argument('--disable-gpu')
            options.add_argument('window-size=1280,800') #

        # try to find the chromedriver binary
        if chromedriver_binary == None:

            # look in current directory
            cur_dir = os.path.dirname(os.path.realpath(__file__))
            cur_dir_files = os.listdir(cur_dir)
            if 'chromedriver' in cur_dir_files:
                chromedriver_binary = os.path.join(cur_dir, 'chromedriver')
            elif os.path.isfile('/usr/lib/chromium-browser/chromedriver'):
                chromedriver_binary = '/usr/lib/chromium-browser/chromedriver'
            else:
                chromedriver_binary = shutil.which('chromedriver')
            
        
        # try to find the chrome/chromium binary
        if chrome_binary == None:
            chrome_binary = shutil.which('chromium-browser')
        
        if not os.path.isfile(chromedriver_binary):
            raise FileNotFoundError("chromedriver binary not found at {}".format(chromedriver_binary))
        if not os.path.isfile(chrome_binary):
            raise FileNotFoundError("chrome binary not found at {}".format(chrome_binary))

        print("creating new chrome instance...") 
        options.binary_location = chrome_binary
        self._driver = webdriver.Chrome(executable_path=chromedriver_binary, chrome_options=options)
        self._driverpid = self._driver.service.process.pid

    def __del__(self):

        if self._driver:
            self._driver.close()
            self._driver.quit()
        
        # TODO maybe use pid to ensure all processes are killed here
        # this does seem to work though
    '''
    def __get(self, url):

        try:
            self._driver.get(url)
        except 
    '''

    def get_url_source(self, url):

        self._driver.get(url)
        return self._driver.page_source


    def get_url_screenshot(self, url):
        
        self._driver.set_window_size(1280,800)
        self._driver.get(url)


        # there's no "save screenshot to a variable,
        # so we have to write it to disk and then read it back in. Gross!
        tempfn = "/tmp/chrome-scr.{}.png".format(random.randrange(10000))

        # if that file exists (highly unlikely), regenerate filename
        while os.path.isfile(tempfn):
            tempfn = "/tmp/chrome-scr.{}.png".format(random.randrange(10000))
        
        self._driver.save_screenshot(tempfn)

        with open(tempfn, mode="rb") as tempfile:
            screenshot = tempfile.read()

        os.remove(tempfn)
        
        return screenshot

