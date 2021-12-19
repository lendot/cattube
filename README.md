# CatTube
### On-demand Video Entertainment For Cats

## 1. Intro
[TODO] Describe this better

With this system you can load up videos your cats like onto a Raspberry Pi
and an ultrasonic sensor will start videos playing when they come in range.
We've had this running for about 3 years in our living room and two of our
cats use it multiple times a day.

## 2. Hardware

- Raspberry Pi 3, 4, Zero, or Zero 2. Zero 2 is recommended over Zero as
it's much faster and the video-start latency is significantly lower.
- HDMI-capable monitor/TV. As mentioned, our cats can get
pretty...aggressive on some videos, so we installed a wall-mount TV bracket
that can swivel
- US-100 ultrasonic sensor. These can be found at several electronics
supply places, including [Adafruit](https://www.adafruit.com/product/4019).
- Wires to connect the sensor to the Pi. If your Pi has headers, then
F-F jumper wires will work. For attaching to my headerless Pi Zero, I
took the header off the US-100 and soldered the wires at both ends

### 2.1. Hookup

Make the following connections between the US-100 and the Raspberry Pi:
| US-100     | Raspberry Pi |
| ---------- | ---------- |
| VCC        | Pin 1 (+3V3) |
| Trig/Tx    | Pin 8 (TXD0 UART, aka GPIO14) |
| Echo/Rx    | Pin 10 (RXD0 UART, aka GPIO15) |
| GND (1)    | Pin 6 (GND) |
| GND (2)    | Pin 9 (GND) |



![wiring connections between Raspberry Pi and US-100](images/cattube-hookup.png)

## 3. Software

Install [Raspberry Pi OS](https://www.raspberrypi.com/software/). Use the
default operating system option.

![Raspberry Pi OS (32-bit) A port of Debian Bullseye with the Raspberry Pi Desktop (Recommended)](images/os-select.png)


Make sure the Pi has internet access and has run its system updates before
continuing. 

Open a terminal and run the following commands:
```
$ git clone https://github.com/lendot/cattube.git
$ cd cattube
$ pip install -r requirements.txt
$ cp cattube.desktop ../Desktop
```

If you want CatTube to automatically start on bootup, also run these:
```
$ mkdir ~/.config/autostart
$ cp cattube.desktop ~/.config/autostart
```

From the desktop menu go to `Preferences` > `Raspberry Pi Configuration`
and do the following:
1. Go to the `Display` tab and set `Screen Blanking` to `Disable`
2. Go to the `Interfaces` tab and set `Serial Port` to `Enable` 

Click Ok and select Yes when asked to reboot.

Open File Manager and go to `Edit` > `Preferences` > `General` and check
"Don't ask options on launch executable file".


### 3.1. Configuration
The configuration file is in `/home/pi/cattube/config.yaml`. It can be edited
with any text editor. The following settings can be tweaked there:

| Setting      | Default                  | Description |
| -------      | -------                  | ----------- |
| video_dir    | /home/pi/Videos          | Location of videos to play |
| distance     | 50                       | Maximum distance (cm) at which sensor will activate | 
| play_clips   | False                    | If False, videos are played in their entirety. If True, random shorter subsections are played at a time |
| clip_duration| 180                      | If play_clips is True, the length of clips (in seconds) to play |
| sensor_device| /dev/ttyS0               | If you need the sensor to to use a different serial device, set it here |
| mute         | False                    | Set to True to mute audio tracks on videos |

play_clips is useful if you have longer videos and don't want the cats to get
bored watching them all the way through. Clip durations betwen about 120s and
300s seem to work well for our cats.

### 3.2. Adding Videos

By default, CatTube looks for videos in `/home/pi/Videos`. mp4 videos are
supported, others formats may be as well. See the Tips For Videos section
below for more information.

You can download videos from a browser or other application on the Pi desktop,
or you can use, say, sftp from another machine (assuming SSH is enabled on
the Pi). If you upload videos from another machine while CatTube is running,
it'll automatically add them to its video pool without requiring a restart.


### 3.3. Troubleshooting

CatTube keeps a log file in `/home/pi/cattube/cattube.log`. Check that first
if anything's amiss.


## 4. Enclosure

At minimum, you'll need some way to hold the sensor in place somewhere
at cat-level while making sure the transmit/receive units are unobstructed.
If you have access to a 3D printer, .stl files are
included for wall-mount enclosures. Ours mounts under the TV.


### 4.1. Sensor Positioning
[TODO]

To help figure out the right distance setting to use in your configuration
file, or to determine if there are any obstacles interfering with a proper
distance reading, you can open up a terminal window and do the following:

```
cd cattube
python3 sensor_readout.py
```

This will bring up a window that continuously updates a display of the
sensor's distance reading. As with the configuration file, values are in
centimeters.


## 5. Tips For Videos
We've found that the best videos are ones filmed from a single, stationary
camera. If the camera is moving, or the video is cutting between multiple
cameras, it gets more confusing for the cats to track. Youtube and other
places have a lot of good single camera little-critters-in-the-woods videos
and the like that our cats take really well to.

I recommend trying a bunch of different types of videos to see what your cat
responds to. In addition to the nature videos ours also like videos of
animated critters and things like balls rolling around. They're even sometimes
interested in gameplay videos from stuff like Tetris or Centipede. A while
back I put an OK Go video on ours just for laughs and it turns out our cats
really like watching it. You never know what might grab their attention.

CatTube uses vlc to play the videos. The version that comes with
Raspberry Pi OS isn't compiled with hardware acceleration enabled, which limits
performance. The Pi 3 I'm testing on can handle standard 1K HD <= 30 FPS fine,
but 4k or higher frame rates give it trouble. If a video is playing really
slowly, or is giving a black screen, you may need to decrease the resolution
and/or frame rate.

