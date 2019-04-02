import time
import random
import serial
from os import listdir
from subprocess import Popen
import videos

# serial device to use to communicate with the US-100
SERIAL_DEVICE = "/dev/ttyS0"

# maximum distance to be considered near (cm)
NEAR_THRESHOLD = 50

# minimum distance to switch from near to away (cm)
AWAY_THRESHOLD = 70


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


near=False

video_process=None

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
            if distance > AWAY_THRESHOLD:
                near = False
                print("Away")
            else:
                video_process = play_video()
        elif distance < NEAR_THRESHOLD:
            # we just moved from away to near
            print("Near detected. Verifying.")
            # do a few more readings to make sure it wasn't a blip
            near = True
            for i in range(3):
                if get_distance() >= NEAR_THRESHOLD:
                    near = False
                    break
                time.sleep(0.25)
            if near:
                print("Verified. Playing video.")
                video_process = play_video()
        time.sleep(1)
