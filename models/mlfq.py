class MultilevelFeedbackQueue:
    def __init__(self, *queues):
        self.queues = queues
        self.processes = []

    def load_processes(self, *iterables: list):
        self.processes = iterables

    def run(self):
        for queue in self.queues:
            queue.load_processes(*self.processes)
            queue.schedule()
            for process in queue.scheduling_algorithm.run():
                print(f"Scheduled: {process}")
    
    # 3 queues with different scheduling algorithms and quantums

