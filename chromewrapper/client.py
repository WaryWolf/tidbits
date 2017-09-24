#!/usr/bin/python

import requests
import json
import base64
import sys


url = sys.argv[1]

print(url)

ret = requests.post('http://127.0.0.1:5001/scrn/', json={'url':url})

j = ret.json()

if j['result'] == 'Error':
    print("Error with your request: {}".format(j['reason']))
    exit()

scrn = base64.b64decode(j['payload'])

with open('result.png',mode="wb") as f:
    f.write(scrn)

