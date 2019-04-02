import random
from os import listdir,stat
from os.path import join

VIDEO_DIR = "/home/pi/videos"

videos = []

last_video_dir_mtime = 0

# gets a random video
def get_video():
    global last_video_dir_mtime,videos

    # see if the contents of the video directory have changed since last scan
    statinfo = stat(VIDEO_DIR)
    if statinfo.st_mtime != last_video_dir_mtime:
        print("video directory changed. Rescanning")
        videos = get_videos()
        last_video_dir_mtime = statinfo.st_mtime

    return random.choice(videos)['filename']

# gets all the videos in the video directory
def get_videos():
    videos=[]
    for f in listdir(VIDEO_DIR):
        if not f.endswith(".mp4"):
            continue
        video={'filename':join(VIDEO_DIR,f)}
        videos.append(video)
    return videos
