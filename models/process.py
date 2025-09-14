class Process:
    def __init__(self, pid, burst_time, arrival_time=0):
        self.pid = pid
        self.name = f"Process-{pid}"
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.waiting_time = 0

    def get_arrival_time(self):
        return self.arrival_time
    
    def get_burst_time(self):
        return self.burst_time
    
    def get_remaining_time(self):
        return self.remaining_time
    
    def update_remaining_time(self,time):
        self.remaining_time -= time

    def __repr__(self):
        return f"{self.name}(BT={self.burst_time}, RT={self.remaining_time}, WT={self.waiting_time})"
