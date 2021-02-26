import time

class Stats:
    """
    Stats recording for video watching behaviors
    """
    
    def __init__(self,stats_file):
        self.stats_file = stats_file

        
    def start_video(self,filename):
        self.total_markers = 0
        self.interest_markers = 0
        self.filename = filename
        self.acc = 0
        self.num_samples = 0
        with open("stats_details.txt","w") as file:
            file.write("{}\n".format(filename))


    def end_video(self):
        """
        Do final stats calculations and append to the stats file
        """
        avg_rate = self.acc/(self.num_samples-1)
        with open(self.stats_file,"a") as file:
            file.write("{},{:.1f}\n".format(self.filename,avg_rate))
        """
        percent_interest = (self.interest_markers/self.total_markers)*100
        with open(self.stats_file,"a") as file:
            file.write("{},{:.1f}\n".format(self.filename,percent_interest))
        """



    def mark_distance(self,distance):
        now = time.time()
        if self.num_samples > 0:
            # calculate the absolute value of the current rate of change
            dt = now - self.last_time
            dd = distance - self.last_reading
            rate = abs(dd/dt)
            self.acc += rate
            with open("stats_details.txt","a") as file:
                file.write("{:.1f}\n".format(rate))

        self.last_time = now
        self.last_reading = distance
        self.num_samples += 1
        
"""
    def mark_interest(self,interested):
        self.total_markers += 1
        if interested:
            self.interest_markers += 1
"""
