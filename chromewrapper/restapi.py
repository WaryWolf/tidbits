#!flask/bin/python
from flask import Flask
from flask import request
from flask import g
import validators

import json
import base64


from chromewrapper import ChromeWrapper

app = Flask(__name__)

# helper function
def is_url(url):

    res = validators.url(url, public=True)

    if not res or not url.startswith('http'):
        print("bad url received: {}".format(url))
        return False

    return True


# helper function
def ret_err(reason):

    if reason == 'BADPARAMS':
        return json.dumps({'result': 'Error','reason': 'Bad parameters'})



def get_chromewrapper():
    if not hasattr(g, 'chromewrapper'):
        g.chromewrapper = ChromeWrapper()
    return g.chromewrapper


@app.teardown_appcontext
def close_chromewrapper(error):
    if hasattr(g, 'chromewrapper'):
        g.chromewrapper = None


@app.route('/')
def index():
    return "Hello world!"


@app.route('/scrn/', methods=['POST'])
def screenshot():

    if 'url' not in request.form or not is_url(request.form['url']):
        return ret_err('BADPARAMS')
   
    url = request.form['url']
    
    print(url)

    c = get_chromewrapper()
    scrndata = c.get_url_screenshot(request.form['url'])
    scrnstring = base64.b64encode(scrndata).decode('utf-8')

    return json.dumps({'result': 'Success', 'payload': scrnstring})
    

@app.route('/source/', methods=['POST'])
def source():

    if 'url' not in request.form or not is_url(request.form['url']):
        return ret_err('BADPARAMS')
   
    url = request.form['url']
    
    print(url)

    c = get_chromewrapper()
    urlsrc = c.get_url_source(url)

    encoded_src = base64.b64encode(urlsrc).decode('utf-8')


if __name__ == '__main__':
    app.run(debug=True, port=5001)


