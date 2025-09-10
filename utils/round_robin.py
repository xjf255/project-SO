def round_robin(*iterables, quantum):
    iterators = [iter(it) for it in iterables]
    while iterators:
        for it in list(iterators):
            for _ in range(quantum):
                try:
                    yield next(it)
                except StopIteration:
                    iterators.remove(it)
                    break