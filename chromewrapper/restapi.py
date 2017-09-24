#!flask/bin/python
from flask import Flask, request, g, render_template, current_app, send_from_directory

import validators

import json
import base64


from chromewrapper import ChromeWrapper

app = Flask(__name__, static_url_path='/static')

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

# helper function
def form_or_json():
    data = request.get_json(silent=True)
    return data if data is not None else request.form

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
    #return "Hello world!"
    #return render_template("test.html")
    return current_app.send_static_file("test.html")


@app.route('/static/<path:path>')
def send_static(path):
	return send_from_directory('static', path)

@app.route('/scrn/', methods=['POST'])
def screenshot():

    # fix to allow both application/x-www-form-urlencoded and application/json requests
    data = form_or_json()

    if 'url' not in data or not is_url(data['url']):
        return ret_err('BADPARAMS')
   
    url = data['url']
    
    print(url)

    c = get_chromewrapper()
    scrndata = c.get_url_screenshot(url)
    scrnstring = base64.b64encode(scrndata).decode('utf-8')

    return json.dumps({'result': 'Success', 'payload': scrnstring})
    

@app.route('/source/', methods=['POST'])
def source():
	

    # fix to allow both application/x-www-form-urlencoded and application/json requests
    data = form_or_json()

    if 'url' not in data or not is_url(data['url']):
        return ret_err('BADPARAMS')
   
    url = data['url']
    
    print(url)

    c = get_chromewrapper()
    urlsrc = c.get_url_source(url)

    encoded_src = base64.b64encode(bytes(urlsrc, 'utf-8')).decode('utf-8')
    
    return json.dumps({'result': 'Success', 'payload': urlsrc})


if __name__ == '__main__':
    app.run(debug=True, port=5001)


