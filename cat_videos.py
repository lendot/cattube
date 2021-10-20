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


class ConfigChangeHandler(PatternMatchingEventHandler):
    # callback for when config file is changed

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

    def on_any_event(self, event):
        logging.info("Config file changed. Reloading")
        app.load_config()



class CatVideos:

    def __init__(self):
        self._init_logging()
        self.config = config.MurderboxConfig(CONFIG_FILE)
        self.load_config()
        self._setup_config_handler()
        self.near = False
        self.playing_video = False
        self.vids = videos.Videos(VIDEO_DIR)
        # self.stats = stats.Stats(join(MURDERBOX_DIR,STATS_FILE))
        self.video = None
        
    def _init_logging(self):
        logging.basicConfig(filename=join(MURDERBOX_DIR,LOG_FILE),
                            filemode="w",
                            level=logging.INFO,
                            format='%(asctime)s %(message)s')
        logging.info("Murderbox starting")


        
    def _in_to_cm(self,inches):
        return inches * 2.54


    def _setup_config_handler(self):
        # set up handler for config file changes
        config_path = join(MURDERBOX_DIR,CONFIG_FILE)
        event_handler = ConfigChangeHandler(self,patterns=[config_path],ignore_patterns=[],ignore_directories=True)
        observer = Observer()
        observer.schedule(event_handler,MURDERBOX_DIR,recursive=False)
        observer.start()

    def load_config(self):
        # (re)load configuration
        
        self.config.load()
        
        self.near_threshold = self.config.get("distance",DEFAULT_NEAR_THRESHOLD)
        self.units = self.config.get("units","cm")
        if self.units != "cm":
            self.near_threshold = self._in_to_cm(self.near_threshold)
        self.away_threshold = self.near_threshold + 10

        logging.info ('near_threshold: {} cm'.format(self.near_threshold))
        logging.info ('away_threshold: {} cm'.format(self.away_threshold))

        self.mute = self.config.get("mute",False)
        logging.info ("mute: {}".format(mute))
            
        self.play_clips = self.config.get("play_clips",False)
        logging.info ("play_clips: {}".format(self.play_clips))
        
        self.clip_duration = self.config.get("clip_duration",180)
        if self.play_clips:
            logging.info("clip_duration: {}".format(self.clip_duration))

            
    def play(self):
        # play a video
        dur = 0
        if self.play_clips:
            dur = self.clip_duration
        self.video=self.vids.play_video(mute=self.mute,clip_duration=dur)
        if self.video is not None:
            stats.start_video(self.video['filename'])
            self.playing_video = True

    def _update_video_playing(self):
        if self.vids.is_finished():
            logging.info("Video done")
            stats.end_video()
            self.playing_video = False
        else:
            # video still playing; track engagement
            distance = sensor.get_distance()
            # stats.mark_interest(distance < away_threshold)
            stats.mark_distance(distance)
            time.sleep(0.25)

    def _update_proximity_wait(self):
        distance = sensor.get_distance()
        if self.near:
            # we were last near; let's see we whether we still are
            if distance > self.away_threshold:
                self.near = False
                logging.info("Away (d={:.1f})".format(distance))
            else:
                logging.info("d={:.1f}".format(distance))
                self.play()
        elif distance < self.near_threshold:
            # we just moved from away to near
            logging.info("Near detected (d={:.1f}) Verifying.".format(distance))
            # do a few more readings to make sure it wasn't a blip
            self.near = True
            for i in range(3):
                dcheck=sensor.get_distance()
                logging.info("  d={:.1f}".format(dcheck))
                if dcheck >= self.near_threshold:
                    self.near = False
                    logging.info("abort")
                    break
                time.sleep(0.1)
            if self.near:
                logging.info("Verified. Playing video.")
                self.play()
        time.sleep(0.25)
            
            
    def update(self):
        # app update loop
        if self.playing_video:
            self._update_video_playing()
        else:
            self._update_proximity_wait()


app = CatVideos()

while True:
    app.update()
