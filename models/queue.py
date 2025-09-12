from models.round_robin import RoundRobin
from models.fcfs import FirstComeFirstServed
class Queue:
  def __init__(self, name, quantum=None):
    self.name = name
    self.scheduling_algorithm = None
    self.iterables = None
    self.quantum = quantum

  def load_processes(self, *iterables: list):
    self.iterables = iterables

  def schedule(self):
    if self.quantum:
      self.scheduling_algorithm = RoundRobin(self.quantum)
    else:
      self.scheduling_algorithm = FirstComeFirstServed(*self.iterables)