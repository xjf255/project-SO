from models.round_robin import RoundRobin
from models.fcfs import FirstComeFirstServed
class Queue:
  def __init__(self, name, *iterables, quantum=None):
    self.name = name
    self.scheduling_algorithm = None
    self.iterables = iterables
    self.quantum = quantum

  def schedule(self):
    if self.quantum:
      self.scheduling_algorithm = RoundRobin(self.iterables, self.quantum)
    else:
      self.scheduling_algorithm = FirstComeFirstServed(*self.iterables)