import serial
import logging
import time

# upper distance limit (cm)
MAX_DISTANCE = 200

# number of readings for the rolling average
NUM_READINGS = 5

# default serial device
SERIAL_DEVICE = "/dev/ttyS0"

DEFAULT_NEAR_THRESHOLD = 50


class DistanceSensor:
    """
    Read and process US_100 sensor distance readings
    """

    def __init__(self,
            serial_device = SERIAL_DEVICE,
            distance = DEFAULT_NEAR_THRESHOLD):
        self.serial_device = serial_device
        self.serial = serial.Serial(self.serial_device)
        self.readings = [MAX_DISTANCE] * NUM_READINGS
        self.readings_idx = 0
        self.near = False
        self.near_threshold = distance
        self.away_threshold = self.near_threshold + 10
        
    def _read_distance(self):
        """
        reads a raw distance from the US-100
        returns distance, in cm
        TODO: handle timeouts, etc.
        """

        # send command to read distane (0x55)
        self.serial.write(bytes([0x55]))
        data = self.serial.read(2)
        cm = (data[1] + (data[0] << 8)) / 10
        logging.debug("raw distance: {:.1f} cm".format(cm))

        # cm = 30

        # sometimes readings go abnormally high (e.g. in the thousands)
        # there's probably a better way to handle this, but for now
        # we'll just clamp it to a reasonable max value
        cm = min(cm,MAX_DISTANCE)
        logging.debug("clamped distance: {:.1f} cm".format(cm))

        return cm

    def get_distance(self):
        """
        Get a smoothed distance reading.
        
        Smoothing is done via a rolling average
        """

        self.readings[self.readings_idx] = self._read_distance()
        self.readings_idx = (self.readings_idx+1) % NUM_READINGS

        readings_sum  = sum(self.readings)

        avg = readings_sum / NUM_READINGS
        
        logging.debug("smoothed distance: {:.1f} cm".format(avg))
        
        return avg

    def update(self):
        """
        Update sensor state

        Returns:
        bool: True if something is detected in front of the sensor 
        """
        distance = self.get_distance()
        if self.near:
            # we were last near; let's see we whether we still are
            if distance > self.away_threshold:
                self.near = False
                logging.info("Away (d={:.1f})".format(distance))
            else:
                logging.info("d={:.1f}".format(distance))
        elif distance < self.near_threshold:
            # we just moved from away to near
            logging.info("Near detected (d={:.1f}) Verifying.".format(distance))
            # do a few more readings to make sure it wasn't a blip
            self.near = True
            for i in range(3):
                dcheck=self.get_distance()
                logging.info("  d={:.1f}".format(dcheck))
                if dcheck >= self.near_threshold:
                    self.near = False
                    logging.info("abort")
                    break
                time.sleep(0.05)
            if self.near:
                logging.info("Verified near.")

        return self.near

