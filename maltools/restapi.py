#!flask/bin/python


import json
import base64
import re

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from flask import Flask, request, g, render_template, current_app, send_from_directory, jsonify
import validators

app = Flask(__name__, static_url_path='/static')

# helper function
def is_url(url):

    res = validators.url(url, public=True)

    if not res or not url.startswith('http'):
        #print("bad url received: {}".format(url))
        return False

    return True


# helper function
def ret_err(reason):

    if reason == 'MISSINGPARAMS':
        return jsonify({'result': 'Error','reason': 'Missing parameters'})
    elif reason == 'BADPARAMS':
        return jsonify({'result': 'Error','reason': 'Malformed or non-sensical parameters'})
    elif reason == 'SERVERROR':
        return jsonify({'result': 'Error','reason': 'Server error'})
    else:
        return jsonify({'result': 'Error','reason': 'Unspecified error'})

# helper function
def getcves(text):    
    cveregex = re.compile('CVE\\-[0-9]{4}\\-[0-9]{4,8}')

    return cveregex.findall(text)


# helper function
def form_or_json():
    data = request.get_json(silent=True)
    return data if data is not None else request.form

def get_chromewrapper():
    if not hasattr(g, 'chromewrapper'):
        g.chromewrapper = ChromeWrapper()
    return g.chromewrapper


@app.route('/')
def index():
    #return "Hello world!"
    #return render_template("test.html")
    return current_app.send_static_file("maltools.html")


@app.route('/static/<path:path>')
def send_static(path):
	return send_from_directory('static', path)

@app.route('/lower/', methods=['POST'])
def lowercase():

    # fix to allow both application/x-www-form-urlencoded and application/json requests
    data = form_or_json()

    if 'text' not in data:
        return ret_err('BADPARAMS')
   
    text = data['text']
    
    return jsonify({'result': 'Success', 'payload': text.lower()})

@app.route('/upper/', methods=['POST'])
def uppercase():

    # fix to allow both application/x-www-form-urlencoded and application/json requests
    data = form_or_json()

    if 'text' not in data:
        return ret_err('BADPARAMS')
   
    text = data['text']
    
    return jsonify({'result': 'Success', 'payload': text.upper()})

@app.route('/defang/', methods=['POST'])
def defang():

    # fix to allow both application/x-www-form-urlencoded and application/json requests
    data = form_or_json()

    if 'url' not in data:
        return ret_err('MISSINGPARAMS')
   
    url = data['url']
    
    if not is_url(url):
        return ret_err('BADPARAMS')

    url = re.sub('\.', '[.]', url)
    url = re.sub('http', 'hXXp', url)

    return jsonify({'result': 'Success', 'payload': url})


@app.route('/refang/', methods=['POST'])
def refang():

    # fix to allow both application/x-www-form-urlencoded and application/json requests
    data = form_or_json()

    if 'url' not in data:
        return ret_err('MISSINGPARAMS')
   
    url = data['url']
    

    # a defanged URL will probably fail this check...
    #if not is_url(url):
    #    return ret_err('BADPARAMS')

    # do the refang!
    url = re.sub(' ', '', url)
    url = re.sub('\[(\.|\:|\/)\]', r'\1', url)
    url = re.sub('hXXp', 'http', url)
    url = re.sub('hxxp', 'http', url)

    return jsonify({'result': 'Success', 'payload': url})

@app.route('/geturls/', methods=['POST'])
def geturls():

    data = form_or_json()

    if 'text' not in data:
        return ret_err('MISSINGPARAMS')

    text = data['text']

    soup = BeautifulSoup(text, 'lxml')

    ret = []
    for link in soup.find_all('a'):
        try:
            link_href = link['href']
        except KeyError:
            continue
        parsed_link = urlparse(link_href)
        ret.append(link_href)

        # construct full urls from relative links in the page
        #if parsed_link.scheme == '' or parsed_link.netloc == '':
        #    ret.append(urljoin(url,link_href))
        #else:
        #    ret.append(link_href)
    
    return jsonify({'result': 'Success', 'payload': ret})



if __name__ == '__main__':
    app.run(debug=True, port=5001)


