# Small app to show sensor distance readings
#

import config
import distance_sensor
import tkinter as tk
import tkinter.font as tkfont

FONT_FAMILY = "DejaVu Sans Mono"

class View(tk.Frame):
    """ Top-level application frame """

    def __init__(self, parent, config, sensor):
        super().__init__(parent)

        self.parent = parent 

        self.config = config
        self.sensor = sensor

        parent.config(bg="black")
        parent.geometry("1000x600")

        self.font = tkfont.Font(family=FONT_FAMILY,size=400)

        self.readout_label = tk.Label(parent,bg="black",fg="#ffffff",font=self.font)
        self.readout_label.pack()

        self.update()


    def update(self):
        """ update sensor reading """
        distance = int(self.sensor.get_distance())
        self.readout_label['text'] = distance
        self.after(200,self.update)



class SensorReadout(tk.Tk):
    """ Main SensorReadout app class """
    def __init__(self):
        super().__init__()
        
        conf = config.CatTubeConfig()

        self.title("CatTube Sensor Readout")

        # set up the sensor
        kwargs = {}
        sensor_device = conf.get("sensor_device")
        if sensor_device is not None:
            kwargs['serial_device'] = sensor_device

        distance = conf.get("distance")
        if distance is not None:
            kwargs['distance'] = distance

        if len(kwargs) == 0:
            sensor = distance_sensor.DistanceSensor()
        else:
            sensor = distance_sensor.DistanceSensor(**kwargs)

        view = View(self,conf,sensor)


def main():

    app = SensorReadout()
    app.mainloop()


if __name__ == "__main__":
    main()

