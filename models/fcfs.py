from models.process import Process
from typing import List, Tuple
class FirstComeFirstServed:
    def execute_processes(self, processes: List[Process], current_time: int) -> List[Tuple[Process, int, int, bool]]:
        """
        Execute processes with FCFS
        Returns: List of (process, start_time, duration, completed)
        """
        results = []
        
        # Sort by arrival time for FCFS
        sorted_processes = sorted([p for p in processes if p.remaining_time > 0], 
                                key=lambda p: p.arrival_time)
        
        for process in sorted_processes:
            # Wait for process arrival if necessary
            current_time = max(current_time, process.arrival_time)
            
            # Record response time
            if process.response_time == -1:
                process.response_time = current_time - process.arrival_time
            
            start_time = current_time
            execution_time = process.remaining_time
            process.remaining_time = 0
            current_time += execution_time
            
            # Calculate final metrics
            process.turnaround_time = current_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            
            results.append((process, start_time, execution_time, True))
        
        return results