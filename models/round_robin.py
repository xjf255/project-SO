from models.process import Process
from typing import List, Tuple
class RoundRobin:
    def __init__(self, quantum: int):
        self.quantum = quantum
    
    def execute_processes(self, processes: List[Process], current_time: int) -> List[Tuple[Process, int, int, bool]]:
        """
        Execute processes with Round Robin
        Returns: List of (process, start_time, duration, completed)
        """
        results = []
        
        if not processes:
            return results
            
        for process in processes[:]:  # Copy list to avoid modification issues
            if process.remaining_time <= 0:
                continue
                
            # Record start time for first execution
            if process.response_time == -1:
                process.response_time = current_time - process.arrival_time
            
            start_time = current_time
            
            # Execute for quantum or remaining time, whichever is smaller
            execution_time = min(self.quantum, process.remaining_time)
            process.remaining_time -= execution_time
            current_time += execution_time
            
            # Check if process completed
            completed = process.remaining_time == 0
            if completed:
                process.turnaround_time = current_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
            
            results.append((process, start_time, execution_time, completed))
        
        return results