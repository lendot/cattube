# CatTube (aka Murderbox)

With this system you can load up videos your cats like onto a Raspberry Pi
and an ultrasonic sensor will let them watch the videos whenever they want.
We've had this running for about 3 years in our living room and two of our
cats use it multiple times a day. Often getting quite violent with the 
monitor when it shows particularly tasty rodents. Hence us calling it the
Murderbox.

## Hardware

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

## Hookup

Make the following connections between the US-100 and the Raspberry Pi:
| US-100     | Raspberry Pi |
| ---------- | ---------- |
| VCC        | Pin 1 (+3V3) |
| Trig/Tx    | Pin 8 (TXD0 UART, aka GPIO14) |
| Echo/Rx    | Pin 10 (RXD0 UART, aka GPIO15) |
| GND (1)    | Pin 9 (GND) |
| GND (2)    | Pin 14 (GND) |


![wiring connections between Raspberry Pi and US-100](images/murderbox-hookup.png)

## Enclosure

At minimum, you'll need some way to hold the sensor in place somewhere
at cat-level while making sure the transmit/receive units are unobstructed.
If you're using a Zero and have access to a 3D printer, .stl files are
included for a wall-mount enclosure. Ours mounts under the TV.

