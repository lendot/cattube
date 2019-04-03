import time
import random
import serial
from os import listdir
from os.path import join
from subprocess import Popen
import videos
import config
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

MURDERBOX_DIR = "/home/pi/src/murderboxws"


# config file
CONFIG_FILE = "config.json"

# serial device to use to communicate with the US-100
SERIAL_DEVICE = "/dev/ttyS0"

# maximum distance to be considered near (cm)
near_threshold = 50

# minimum distance to switch from near to away (cm)
away_threshold = 70


serial1 = serial.Serial(SERIAL_DEVICE)


buffer_len=10
value_buffer=[0]*buffer_len
value_idx=0


# reads a distance from the US-100
# returns distnace, in cm
def get_distance():
    # TODO: handle timeouts, etc.
    # send command (0x55) to read distance
    serial1.write(bytes([0x55]))
    data = serial1.read(2)
    cm = (data[1] + (data[0] << 8)) / 10
    return cm
    
def play_video():
    video_file=videos.get_video()
    omxp = Popen(['omxplayer','-b',video_file])
    return omxp

def in_to_cm(inches):
    return inches * 2.54

def load_config():
    global conf,near_threshold,away_threshold
    conf = config.load_config(CONFIG_FILE)
    near_threshold = conf['distance']
    if conf['units'] != "cm":
        near_threshold = in_to_cm(near_threshold)
    away_threshold = near_threshold + 20
    print ('near_threshold: ' + str(near_threshold))
    print ('away_threshold: ' + str(away_threshold))

class ConfigChangeHandler(PatternMatchingEventHandler):
    def on_any_event(self, event):
        print("Config file changed. Reloading")
        load_config()



near=False

video_process=None

load_config()


# set up handler for config file changes
config_path = join(MURDERBOX_DIR,CONFIG_FILE)
event_handler = ConfigChangeHandler(patterns=[config_path],ignore_patterns=[],ignore_directories=True)
observer = Observer()
observer.schedule(event_handler,MURDERBOX_DIR,recursive=False)
observer.start()
               

while True:
    if video_process is not None:
        # video is playing
        if video_process.poll() is not None:
            # video is done playing
            video_process = None
        else:
            time.sleep(0.2)
    else:
        distance = get_distance()
        if near:
            # we were last near; let's see we whether we still are
            if distance > away_threshold:
                near = False
                print("Away")
            else:
                video_process = play_video()
        elif distance < near_threshold:
            # we just moved from away to near
            print("Near detected. Verifying.")
            # do a few more readings to make sure it wasn't a blip
            near = True
            for i in range(3):
                if get_distance() >= near_threshold:
                    near = False
                    break
                time.sleep(0.25)
            if near:
                print("Verified. Playing video.")
                video_process = play_video()
        time.sleep(1)
