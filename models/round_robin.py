from models.process import Process
import time
class RoundRobin:
    def __init__(self, quantum):
        self.quantum = quantum

    def run(self, *iterables: list[Process]):
        now = time.time()
        print(f"RoundRobin started at {now}")
        if iterables is None or len(iterables) == 0:
            return 0
        
        iterators = [iter(it) for it in iterables]
        while iterators:
            for it in list(iterators):
                it.__repr__()
                arrived_process = next(it, None)
                for _ in range(self.quantum):
                    try:
                        yield next(it)
                    except StopIteration:
                        iterators.remove(it)
                        break