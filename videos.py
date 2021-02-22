import random
import logging
from os import listdir,stat
from os.path import join
import os
import psutil
from tinytag import TinyTag

VIDEO_DIR = "/home/pi/videos"

videos = []

last_video_dir_mtime = 0

# gets a random video
def get_video():
    global last_video_dir_mtime,videos

    # see if the contents of the video directory have changed since last scan
    statinfo = stat(VIDEO_DIR)
    if statinfo.st_mtime != last_video_dir_mtime:
        logging.info("video directory changed. Rescanning")
        videos = get_videos()
        last_video_dir_mtime = statinfo.st_mtime

    return random.choice(videos)

# gets all the videos in the video directory
def get_videos():
    videos=[]
    for f in listdir(VIDEO_DIR):
        if not f.endswith(".mp4"):
            continue
        absolute_path = join(VIDEO_DIR,f)

        # get the video file metadata
        tag = TinyTag.get(absolute_path)
        video={'filename':absolute_path,
               'duration':tag.duration}
        videos.append(video)
    return videos

# remove the video with the given filename
def remove(video):
    path = join(VIDEO_DIR,video)
    try:
        os.remove(path)
    except FileNotFoundError:
        logging.error("File not found: "+path)



class Videos:
    """
    Play and manage videos
    """

    player = None
    
    def __init__(self,video_dir):
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

    
    def remove(self,video):
        """
        remove the video with the given filename
        """
        path = join(self.video_dir,video)
        try:
            os.remove(path)
        except FileNotFoundError:
            logging.error("File not found: "+path)


    def _terminate_process(self,pid):
        """
        terminate a process and all its children
        """
        p = psutil.Process(pid)
        children = p.children()
        for child in children:
            child.terminate()
        gone, alive = psutil.wait_procs(children,timeout=3)
        for child in alive:
            # process still lingering; forefully kill it
            logging("Child PID {} didn't terminate. Killing.".format(child.pid))
            child.kill()
        
        p.terminate()
        # do a wait and p.kill() if process sticks around?

            
    def play_video(self,mute=False,clip_duration=0):
        """
        select a random video and play it
        """

        play_clips = clip_duration > 0

        # get a random video to play
        video = self.videos.get_video()
        video_file = video['filename']
        
        args = ['/usr/bin/omxplayer','-b','--no-osd']

        if mute:
            # not sure how reliable omxplayer -n -1 is, but not
            # sure of any better alternatives for muting
            args.extend(["-n","-1"])


        def omxplayer_timestamp(s):
            # convert number of seconds to an omxplayer HH:MM:SS timestamp
            ts = datetime.timedelta(seconds=s)
            return str(ts)
        
        video_duration = int(video['duration'])

        # default: play entire video
        timestamp = omxplayer_timestamp(0)
        duration = video_duration
    
        if play_clips and video_duration > clip_duration::
            # pick a random section of the video to play
            start = random.randint(0,video_duration-clip_duration)
            duration = clip_duration
            timestamp = omxplayer_timestamp(start)
            args.extend(["--pos",timestamp])

        args.append(video_file)

        logging.info("playing {}@{}".format(video_file,timestamp))

        try:
            self.video_player = Popen(args)
        except Exception:
            logging.exception("process creation failed: ")
            logging.info(args)
            return None

        stats.start_video(video_file)

        self.player_duration = duration
        self.player_start = time.time()
    
        return self.player
