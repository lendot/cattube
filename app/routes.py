from flask import render_template,send_from_directory
from os import listdir
from app import app

VIDEO_DIR = "/home/pi/videos"

@app.route('/')
def index():
    videos=[f for f in listdir(VIDEO_DIR) if f.endswith(".mp4")]
    return render_template('index.html',videos=videos)
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
