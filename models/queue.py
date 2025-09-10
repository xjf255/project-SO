class Queue:
  def __init__(self, name, scheduling_algorithm, *iterables, quantum=None):
      self.name = name
      self.scheduling_algorithm = scheduling_algorithm
      self.iterables = iterables
      self.quantum = quantum