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
    conf = config.load_config(CONFIG_FILE)

    # load parameters from the POST request
    distance = int(request.form.get('distance'))
    units = request.form.get('units')
    mute = request.form.get('mute') == 'true'

    # update configuration settings
    conf['distance'] = distance
    conf['units'] = units
    conf['mute'] = mute
    config.save_config(conf,CONFIG_FILE)

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
