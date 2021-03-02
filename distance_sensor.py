import serial
import logging
import time

# upper distance limit (cm)
MAX_DISTANCE = 100

# number of readings for the rolling average
NUM_READINGS = 5

class DistanceSensor:
    """
    Read and process US_100 sensor distance readings
    """

    def __init__(self,serial_device):
        self.serial_device = serial_device
        self.serial = serial.Serial(self.serial_device)
        self.readings = [MAX_DISTANCE] * NUM_READINGS
        self.readings_idx = 0
        
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
                                                                                                
