def first_come_first_served(*iterables):
    for it in iterables:
        yield from it