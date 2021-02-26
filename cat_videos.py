import time
from os.path import join
import logging
import videos
import config
import distance_sensor
import stats
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

MURDERBOX_DIR = "/home/pi/src/murderboxws"

VIDEO_DIR = "/home/pi/videos"

STATS_FILE = "stats.csv"

LOG_FILE = "cat_videos.log"

# config file
CONFIG_FILE = "config.json"

# serial device to use to communicate with the US-100
SERIAL_DEVICE = "/dev/ttyS0"
sensor = distance_sensor.DistanceSensor(SERIAL_DEVICE)


# maximum distance to be considered near (cm)
near_threshold = 50
DEFAULT_NEAR_THRESHOLD = 50

# minimum distance to switch from near to away (cm)
away_threshold = 70


mute = False
play_clips = False

stats = stats.Stats(join(MURDERBOX_DIR,STATS_FILE))

def in_to_cm(inches):
    return inches * 2.54

def load_config():
    # TODO: clean this up, do defaults better
    global conf,near_threshold,away_threshold,mute,play_clips
    conf = config.load_config(CONFIG_FILE)
    near_threshold = conf['distance']
    if conf['units'] != "cm":
        near_threshold = in_to_cm(near_threshold)
    away_threshold = near_threshold + 20
    logging.info ('near_threshold: ' + str(near_threshold))
    logging.info ('away_threshold: ' + str(away_threshold))

    mute = conf['mute']
    logging.info ("mute: " + str(mute))

    play_clips = conf['play_clips']
    logging.info ("play_clips: {}".format(play_clips))
    if play_clips:
        logging.info("clip_duration: {}".format(conf['clip_duration']))
    

class ConfigChangeHandler(PatternMatchingEventHandler):
    def on_any_event(self, event):
        logging.info("Config file changed. Reloading")
        load_config()



near=False


# set up logging
logging.basicConfig(filename=join(MURDERBOX_DIR,LOG_FILE),
                    filemode="w",
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

v = videos.Videos(VIDEO_DIR)


def play():
    # play a video
    global playing_video
    dur = 0
    if play_clips:
        dur = conf['clip_duration']
    video=v.play_video(mute=mute,clip_duration=dur)
    if video is not None:
        stats.start_video(video['filename'])
        playing_video = True


playing_video = False

while True:
    if playing_video:
        if v.is_finished():
            logging.info("Video done")
            stats.end_video()
            playing_video = False
        else:
            # video still playing; track engagement
            distance = sensor.get_distance()
            # stats.mark_interest(distance < away_threshold)
            stats.mark_distance(distance)
            time.sleep(0.5)
    else:
        distance = sensor.get_distance()
        if near:
            # we were last near; let's see we whether we still are
            if distance > away_threshold:
                near = False
                logging.info("Away (d={:.1f})".format(distance))
            else:
                logging.info("d={:.1f}".format(distance))
                play()
        elif distance < near_threshold:
            # we just moved from away to near
            logging.info("Near detected (d={:.1f}) Verifying.".format(distance))
            # do a few more readings to make sure it wasn't a blip
            near = True
            for i in range(3):
                dcheck=sensor.get_distance()
                logging.info("  d={:.1f}".format(dcheck))
                if dcheck >= near_threshold:
                    near = False
                    logging.info("abort")
                    break
                time.sleep(0.1)
            if near:
                logging.info("Verified. Playing video.")
                play()
        time.sleep(0.25)



"""
class CatVideos:

    def __init__(self):
        self._init_logging()
        self.config = config.MurderboxConfig(CONFIG_FILE)
        self._load_config()
        self.near = False
        self.playing_video = False
        self.vids = videos.Videos(VIDEO_DIR)
        self.stats = stats.Stats(join(MURDERBOX_DIR,STATS_FILE))
        self.video = None
        
    def _init_logging(self):
        logging.basicConfig(filename=join(MURDERBOX_DIR,LOG_FILE),
                            filemode="w",
                            level=logging.INFO,
                            format='%(asctime)s %(message)s')
        logging.info("Murderbox starting")


        
    def _in_to_cm(self,inches):
        return inches * 2.54


    def _load_config(self):
        self.near_threshold = self.config.get("distance",DEFAULT_NEAR_THRESHOLD)
        self.units = self.config.get("units","cm")
        if self.units != "cm":
            self.near_threshold = self._in_to_cm(self.near_threshold)
        self.away_threshold = self.near_threshold + 20

        logging.info ('near_threshold: {} cm'.format(self.near_threshold))
        logging.info ('away_threshold: {} cm'.format(self.away_threshold))

        self.mute = self.config.get("mute",False)
        logging.info ("mute: {}".format(mute))
            
        self.play_clips = self.config.get("play_clips",False)
        logging.info ("play_clips: {}".format(self.play_clips))
        
        self.clip_duration = self.config.get("clip_duration",180)
        if self.play_clips:
            logging.info("clip_duration: {}".format(self.clip_duration))
        
    def play():
        # play a video
        dur = 0
        if self.play_clips:
            dur = self.clip_duration
        self.video=self.vids.play_video(mute=self.mute,clip_duration=dur)
        if self.video is not None:
            self.stats.start_video(self.video['filename'])
            self.playing_video = True
"""
