import random
import logging
from os import listdir,stat
from os.path import join
import os
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

