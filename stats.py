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


    def end_video(self):
        percent_interest = (self.interest_markers/self.total_markers)*100
        with open(self.stats_file,"a") as file:
            file.write("{},{:.1f}\n".format(self.filename,percent_interest))


    def mark_interest(self,interested):
        self.total_markers += 1
        if interested:
            self.interest_markers += 1
