import serial

class DistanceSensor:
    """
    Read and process US_100 sensor distance readings
    """

    def __init__(self,serial_device):
        self.serial_device = serial_device
        self.serial = serial.Serial(self.serial_device)

        
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
        return cm

    def get_distance(self):
        """
        Get a smoothed distance reading.
        
        Several readings are taken in succession and averaged after discarding
        min/max values
        """
        num_readings=5
        acc=0
        min_reading = 0xffff
        max_reading = -0xffff
        for i in range (num_readings):
            reading = self._read_distance()
            acc += reading
            if reading < min_reading:
                min_reading = reading
            elif reading > max_reading:
                max_reading = reading
            time.sleep(0.005)

        # remove min/max readings
        acc -= min_reading
        acc -= max_reading
        distance = acc/(num_readings-2)
        logging.debug("smoothed distance: {:.1f} cm".format(distance))
        
        return distance
                                                                                                
