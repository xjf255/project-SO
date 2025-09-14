from models.process import Process
from models.round_robin import RoundRobin
from models.fcfs import FirstComeFirstServed
from typing import List, Optional, Tuple
class Queue:
    def __init__(self, name: str, quantum: Optional[int] = None, priority: int = 0):
        self.name = name
        self.quantum = quantum
        self.priority = priority
        self.processes: List[Process] = []
        
        # Set scheduling algorithm based on quantum
        if quantum:
            self.scheduling_algorithm = RoundRobin(quantum)
        else:
            self.scheduling_algorithm = FirstComeFirstServed()
    
    def add_process(self, process: Process):
        """Add a process to this queue"""
        self.processes.append(process)
    
    def remove_process(self, process: Process):
        """Remove a process from this queue"""
        if process in self.processes:
            self.processes.remove(process)
    
    def has_ready_processes(self, current_time: int) -> bool:
        """Check if there are processes ready to run"""
        return any(p.remaining_time > 0 and p.arrival_time <= current_time 
                  for p in self.processes)
    
    def get_ready_processes(self, current_time: int) -> List[Process]:
        """Get processes that are ready to run"""
        return [p for p in self.processes 
                if p.remaining_time > 0 and p.arrival_time <= current_time]
    
    def execute(self, current_time: int) -> List[Tuple[Process, int, int, bool]]:
        """Execute ready processes in this queue"""
        ready_processes = self.get_ready_processes(current_time)
        return self.scheduling_algorithm.execute_processes(ready_processes, current_time)