from flask import render_template,send_from_directory,request,redirect
from os import listdir
from app import app
import config

VIDEO_DIR = "/home/pi/videos"

CONFIG_FILE = "config.json"

@app.route('/')
def index():
    videos=[f for f in listdir(VIDEO_DIR) if f.endswith(".mp4")]
    conf = config.load_config(CONFIG_FILE)
    return render_template('index.html',videos=videos,config=conf)


@app.route('/update',methods=['POST'])
def update():
    print("got here")
    distance = request.form.get('distance')
    print("got here 2")
    units = request.form.get('units')
    print(distance)
    print(units)
    return redirect("/")

'''
@app.route('/css/<path:path>')
def send_css(path):
    print("request: "+path)
    return send_from_directory('/css',path)

@app.route('/js/<path:path>')
def send_js(path):
    print("request: "+path)
    return send_from_directory('/js',path)
'''
