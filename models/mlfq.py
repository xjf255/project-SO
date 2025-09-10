class MultilevelFeedbackQueue:
    def __init__(self, *queues, scheduling_algorithm):
        self.queues = queues
        self.scheduling_algorithm = scheduling_algorithm

    def schedule(self):
        return self.scheduling_algorithm(*self.queues)