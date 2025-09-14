from models.process import Process
from typing import List
import time
class MultilevelFeedbackQueue:
    def __init__(self, *queue_configs):
        # Sort queues by priority (lower number = higher priority)
        self.queues = queue_configs
        self.all_processes: List[Process] = []
        self.current_time = 0
    
    def load_processes(self, processes: List[Process]):
        """Load all processes into the highest priority queue initially"""
        self.all_processes = processes.copy()
        
        # Add all processes to the highest priority queue (first queue)
        if self.queues:
            for process in processes:
                # Reset process state
                process.remaining_time = process.burst_time
                process.response_time = -1
                process.waiting_time = 0
                process.turnaround_time = 0
                
                self.queues[0].add_process(process)
    
    def promote_processes(self):
        """Move processes that haven't run recently to higher priority queues"""
        # This is a simplified promotion strategy
        # In practice, you might want more sophisticated aging mechanisms
        pass
    
    def demote_process(self, process: Process, from_queue_index: int):
        """Move a process to a lower priority queue"""
        if from_queue_index < len(self.queues) - 1:
            # Remove from current queue
            self.queues[from_queue_index].remove_process(process)
            # Add to next lower priority queue
            self.queues[from_queue_index + 1].add_process(process)
            print(f"  → {process.name} demoted to {self.queues[from_queue_index + 1].name}")
    
    def run(self, simulate_time: bool = False):
        """Execute the multilevel feedback queue scheduling"""
        print(f"\n=== Multilevel Feedback Queue Scheduling ===")
        
        # Print queue configuration
        for i, queue in enumerate(self.queues):
            print(f"{queue.quantum}")
            quantum_info = f" (Quantum: {queue.quantum})" if queue.quantum else " (FCFS)"
            print(f"Queue {i}: {queue.name}{quantum_info}")
        
        print(f"\nInitial processes: {[p.name for p in self.all_processes]}")
        print("\nExecution Timeline:")
        
        execution_log = []
        
        while any(p.remaining_time > 0 for p in self.all_processes):
            executed_any = False
            
            # Check queues in priority order
            for queue_index, queue in enumerate(self.queues):
                if not queue.has_ready_processes(self.current_time):
                    continue
                
                print(f"\nTime {self.current_time}: Executing {queue.name}")
                
                # Execute processes in this queue
                results = queue.execute(self.current_time)
                
                for process, start_time, duration, completed in results:
                    end_time = start_time + duration
                    
                    print(f"  {start_time}-{end_time}: {process.name} "
                          f"(remaining: {process.remaining_time})")
                    
                    execution_log.append({
                        'queue': queue.name,
                        'process': process.name,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': duration,
                        'remaining': process.remaining_time
                    })
                    
                    # Update current time
                    self.current_time = end_time
                    executed_any = True
                    
                    # If process not completed and used full quantum, demote it
                    if not completed and queue.quantum and duration == queue.quantum:
                        self.demote_process(process, queue_index)
                    
                    # Optional: simulate real time
                    if simulate_time:
                        time.sleep(0.1)
                
                # Only execute one queue per time slice in MLFQ
                if results:
                    break
            
            # Prevent infinite loops
            if not executed_any:
                # Jump to next process arrival time
                next_arrival = min((p.arrival_time for p in self.all_processes 
                                  if p.arrival_time > self.current_time and p.remaining_time > 0),
                                 default=self.current_time + 1)
                self.current_time = next_arrival
        
        # Calculate and display final metrics
        self.display_final_metrics()
        return execution_log
    
    def display_final_metrics(self):
        """Display final scheduling metrics"""
        print(f"\n=== Final Results ===")
        
        completed_processes = [p for p in self.all_processes if p.remaining_time == 0]
        
        if not completed_processes:
            print("No processes completed!")
            return
        
        print(f"{'Process':<12} {'Burst':<6} {'Wait':<6} {'Turnaround':<10} {'Response':<8}")
        print("-" * 50)
        
        total_waiting = 0
        total_turnaround = 0
        total_response = 0
        
        for process in completed_processes:
            print(f"{process.name:<12} {process.burst_time:<6} {process.waiting_time:<6} "
                  f"{process.turnaround_time:<10} {process.response_time:<8}")
            
            total_waiting += process.waiting_time
            total_turnaround += process.turnaround_time
            total_response += process.response_time
        
        n = len(completed_processes)
        print("-" * 50)
        print(f"Average:     {'':<6} {total_waiting/n:<6.1f} "
              f"{total_turnaround/n:<10.1f} {total_response/n:<8.1f}")