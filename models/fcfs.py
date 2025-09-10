class FirstComeFirstServed:
    def __init__(self, *iterables):
        self.iterables = iterables
    
    def run(self):
        for it in self.iterables:
            yield from it