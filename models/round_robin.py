class RoundRobin:
    def __init__(self, quantum):
        self.quantum = quantum

    def run(self, *iterables):
        if iterables is None or len(iterables) == 0:
            return 0
        
        iterators = [iter(it) for it in iterables]
        while iterators:
            for it in list(iterators):
                for _ in range(self.quantum):
                    try:
                        yield next(it)
                    except StopIteration:
                        iterators.remove(it)
                        break