import logging
import config
import videos
import distance_sensor
import tkinter as tk
import vlc
import random
import time

LOG_FILE = "cattube.log"

# number of seconds to wait after inactivity before stopping the running video
# 0 = don't time out 
DEFAULT_IDLE_TIMEOUT = 15

class View(tk.Frame):
    """ Top-level application frame """

    def __init__(self, parent, config, sensor, vids):
        super().__init__(parent)

        self.parent =parent 

        self.config = config
        self.sensor = sensor
        self.vids = vids

        self.video_playing = False
        self.video_end_timer = None
        self.idle = False

        self.play_clips = self.config.get("play_clips",False)
        logging.info ("play_clips: {}".format(self.play_clips))
        self.clip_duration = self.config.get("clip_duration",180)
        if self.play_clips:
            logging.info("clip_duration: {}".format(self.clip_duration))

        self.idle_timeout = self.config.get("idle_timeout",DEFAULT_IDLE_TIMEOUT)
        logging.info("idle_timeout: {}".format(self.idle_timeout))

        # make window full screen
        w,h = parent.winfo_screenwidth(), parent.winfo_screenheight()
        parent.geometry("{0}x{1}+0+0".format(w,h))
        # get rid of title bar, etc.
        parent.overrideredirect(1)
        parent.config(bg="black",cursor="none")

        self.video_frame = tk.Frame(parent,bg="black")
        self.video_frame.pack(expand=True,fill='both')

        # set up handlers for keypresses and mouse clicks
        parent.bind("<Key>",self.key_pressed)
        parent.bind("<Button>",self.mouse_click)


        # set up video player frame
        self.vlc_instance = vlc.Instance("--no-xlib")
        self.video_player = self.vlc_instance.media_player_new()
        self.video_player.set_xwindow(self.video_frame.winfo_id()) # attach vlc to this window

        self.update()


    def key_pressed(self,event):
        self.parent.destroy()

    def mouse_click(self,event):
        self.parent.destroy() 

    def update(self):
        """ update sensor status """
        active = self.sensor.update()
        if active:
            self.idle = False
            if self.video_playing:
                pass
            else:
                self.play_video()
        elif self.video_playing and self.idle_timeout > 0:
            if self.idle:
                now = time.monotonic()
                if now - self.idle_start > self.idle_timeout:
                    # kill the running video 
                    if self.video_end_timer is not None:
                        self.after_cancel(self.video_end_timer)
                    self.video_end()
            else:
                logging.info("Idle detected")
                self.idle_start = time.monotonic() 
                self.idle = True
            
        self.after(100,self.update)


    def video_end(self):
        """ time to make video stop """
        self.video_player.stop()
        logging.info("video ended")
        self.video_playing = False
        self.idle = False
        self.video_end_timer = None
        self.vlc_media.release()
        self.vlc_media = None

    def play_video(self):
        """ find a video to play and start playing it """
        video = self.vids.get_video()

        video_duration = int(video['duration'])

        # default: play entire video
        start = 0
        seek = 0
        duration = video_duration

        if self.play_clips and video_duration > self.clip_duration:
            # pick a random section of the video to play
            start = random.randint(0,video_duration-self.clip_duration)
            duration = self.clip_duration
            seek = start*1000 

        self.vlc_media = self.vlc_instance.media_new(video['filename'])
        self.video_player.set_media(self.vlc_media)

        logging.info("Playing video {} seek={}s duration={}s".format (video['filename'],start,duration))

        if self.video_player.play() == -1:
            logging.error("Can't play video")
            return

        # can't seek until after video starts playing
        self.video_player.set_time(seek)

        self.video_playing = True
        self.idle = False

        # set up callback to stop video play after duration
        self.video_end_timer = self.after(int(duration*1000),self.video_end)


class CatTube(tk.Tk):
    """ Main CatTube app class """
    def __init__(self):
        super().__init__()
        
        conf = config.CatTubeConfig()

        # set up the sensor
        kwargs = {}
        sensor_device = conf.get("sensor_device")
        if sensor_device is not None:
            kwargs['serial_device'] = sensor_device

        distance = conf.get("distance")
        if distance is not None:
            kwargs['distance'] = distance

        if len(kwargs) == 0:
            sensor = distance_sensor.DistanceSensor()
        else:
            sensor = distance_sensor.DistanceSensor(**kwargs)

        video_dir = conf.get("video_dir")
        if video_dir is None:
            vids = videos.Videos()
        else:
            vids = videos.Videos(video_dir = video_dir)

        # create view object(config,distance,video)
        view = View(self,conf,sensor,vids)


def main():

    logging.basicConfig(filename=LOG_FILE,
                        level=logging.INFO,
                        filemode="w",
                        format='%(asctime)s %(message)s')
    logging.info("cattube starting")
    
    app = CatTube()
    app.mainloop()

    logging.info("cattube exiting")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("main exception")
    finally:
        logging.info("Exiting")

