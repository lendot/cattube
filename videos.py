import random
import logging
from os import listdir,stat
from os.path import join
from tinytag import TinyTag

# default video dir
VIDEO_DIR = "/home/pi/videos"

class Videos:
    """
    Play and manage videos
    """

    player = None
    
    def __init__(self,video_dir = VIDEO_DIR):
        self.video_dir = video_dir
        self.last_video_dir_mtime = 0
        self.get_videos()


    def get_video(self):
        """
        select a random video to play
        """

        # see if the contents of the video directory have changed since last scan
        statinfo = stat(self.video_dir)
        if statinfo.st_mtime != self.last_video_dir_mtime:
            logging.info("video directory changed. Rescanning")
            self.get_videos()
            self.last_video_dir_mtime = statinfo.st_mtime

        return random.choice(self.videos)


    def get_videos(self):
        """
        get info on all the videos in the video directory
        """
        self.videos=[]
        for f in listdir(self.video_dir):
            if not f.endswith(".mp4"):
                continue
            absolute_path = join(self.video_dir,f)

            # get the video file metadata
            tag = TinyTag.get(absolute_path)
            video={'filename':absolute_path,
                   'duration':tag.duration}
            self.videos.append(video)
        return self.videos

