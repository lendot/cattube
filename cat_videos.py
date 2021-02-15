import time
import random
import serial
from os import listdir
from os.path import join
from subprocess import Popen
import logging
import videos
import config
import stats
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

MURDERBOX_DIR = "/home/pi/src/murderboxws"

STATS_FILE = "stats.csv"

LOG_FILE = "cat_videos.log"

# config file
CONFIG_FILE = "config.json"

# serial device to use to communicate with the US-100
SERIAL_DEVICE = "/dev/ttyS0"

# maximum distance to be considered near (cm)
near_threshold = 40

# minimum distance to switch from near to away (cm)
away_threshold = 60


serial1 = serial.Serial(SERIAL_DEVICE)


buffer_len=10
value_buffer=[0]*buffer_len
value_idx=0

mute = False

stats = stats.Stats(MURDERBOX_DIR+"/"+STATS_FILE)


# reads a distance from the US-100
# returns distnace, in cm
def read_distance():
    # TODO: handle timeouts, etc.
    # send command (0x55) to read distance
    serial1.write(bytes([0x55]))
    data = serial1.read(2)
    cm = (data[1] + (data[0] << 8)) / 10
    logging.debug("raw distance: {:.1f} cm".format(cm))
    return cm


# get a smoothed distance reading
def get_distance():
    num_readings=5
    acc=0
    min_reading = 0xffff
    max_reading = -0xffff
    for i in range (num_readings):
        reading = read_distance()
        acc += reading
        if reading < min_reading:
            min_reading = reading
        elif reading > max_reading:
            max_reading = reading
        time.sleep(0.005)

    # remove min/max readings
    acc -= min_reading
    acc -= max_reading
    
    distance = acc/(num_readings-2)
    logging.debug("smoothed distance: {:.1f} cm".format(distance))
    
    return distance


def play_video():
    global stats
    video_file=videos.get_video()

    logging.info("playing "+video_file)
    
    args = ['omxplayer','-b']

    if mute:
        # not sure how reliable omxplayer -n -1 is, but not
        # sure of any better alternatives for muting
        args.extend(["-n","-1"])

    args.append(video_file)

    omxp = Popen(args)
    stats.start_video(video_file)
    
    return omxp

def in_to_cm(inches):
    return inches * 2.54

def load_config():
    global conf,near_threshold,away_threshold,mute
    conf = config.load_config(CONFIG_FILE)
    near_threshold = conf['distance']
    if conf['units'] != "cm":
        near_threshold = in_to_cm(near_threshold)
    away_threshold = near_threshold + 20
    logging.info ('near_threshold: ' + str(near_threshold))
    logging.info ('away_threshold: ' + str(away_threshold))

    mute = conf['mute']
    logging.info ("mute: " + str(mute))

class ConfigChangeHandler(PatternMatchingEventHandler):
    def on_any_event(self, event):
        logging.info("Config file changed. Reloading")
        load_config()



near=False

video_process=None

# set up logging
logging.basicConfig(filename=MURDERBOX_DIR+"/"+LOG_FILE,
                    level=logging.INFO,
                    format='%(asctime)s %(message)s')
logging.info("Murderbox starting")



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
            logging.info("Video done")
            video_process = None
            stats.end_video()
        else:
            distance = get_distance()
            stats.mark_interest(distance < away_threshold)
            time.sleep(0.5)
    else:
        distance = get_distance()
        if near:
            # we were last near; let's see we whether we still are
            if distance > away_threshold:
                near = False
                logging.info("Away (d={:.1f})".format(distance))
            else:
                video_process = play_video()
        elif distance < near_threshold:
            # we just moved from away to near
            logging.info("Near detected (d={:.1f}) Verifying.".format(distance))
            # do a few more readings to make sure it wasn't a blip
            near = True
            for i in range(3):
                dcheck=get_distance()
                logging.info("  d={:.1f}".format(dcheck))
                if dcheck >= near_threshold:
                    near = False
                    logging.info("abort")
                    break
                time.sleep(0.05)
            if near:
                logging.info("Verified. Playing video.")
                video_process = play_video()
        time.sleep(0.25)
