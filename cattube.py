import logging
import config
import videos
import distance_sensor
import tkinter as tk
import vlc
import random

LOG_FILE = "cattube.log"

class View(tk.Frame):
    """ Top-level application frame """

    def __init__(self, parent, config, sensor, vids):
        super().__init__(parent)

        self.parent =parent 

        self.config = config
        self.sensor = sensor
        self.vids = vids

        self.video_playing = False

        self.play_clips = self.config.get("play_clips",False)
        logging.info ("play_clips: {}".format(self.play_clips))
        self.clip_duration = self.config.get("clip_duration",180)
        if self.play_clips:
            logging.info("clip_duration: {}".format(self.clip_duration))


        # make window full screen
        w,h = parent.winfo_screenwidth(), parent.winfo_screenheight()
        parent.geometry("{0}x{1}+0+0".format(w,h))
        # get rid of title bar, etc.
        # parent.overrideredirect(1)
        parent.config(bg="black")

        self.video_frame = tk.Frame(parent)
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
        if active and not self.video_playing:
            self.play_video()
        self.after(100,self.update)


    def video_end(self):
        """ time to make video stop """
        self.video_player.stop()
        self.video_playing = False

    def play_video(self):
        """ find a video to play and start playing it """
        video = self.vids.get_video()

        video_duration = int(video['duration'])

        # default: play entire video
        seek = 0.0
        duration = video_duration

        if self.play_clips and video_duration > self.clip_duration:
            # pick a random section of the video to play
            start = random.randint(0,video_duration-self.clip_duration)
            duration = self.clip_duration
            seek = float(start)

        self.vlc_media = self.vlc_instance.media_new(video['filename'])
        self.video_player.set_media(self.vlc_media)

        logging.info("Playing video {}".format (video['filename']))

        if self.video_player.play() == -1:
            logging.error("Can't play video")
            return

        self.video_playing = True

        # set up callback to stop video play after duration
        self.after(int(duration*1000),self.video_end)


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
