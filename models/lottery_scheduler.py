import random
from typing import List, Tuple, Dict, Any

from models.process import Process

class LotteryScheduler:

    def __init__(self, config: Dict[str, Any]):
        self.semilla = config.get('parametros', {}).get('semilla')
        
        self.procesos = []
        for p_data in config.get('procesos', []):
            proceso = Process(
                pid=p_data['pid'], 
                burst_time=p_data['rafaga'], 
                arrival_time=p_data.get('llegada', 0)
            )
            proceso.tickets = p_data.get('boletos', 0)
            self.procesos.append(proceso)

    def _execute_tick(self, ready_queue: List[Process], current_time: int) -> Tuple[Process, int, int, bool] | None:
        if not ready_queue:
            return None

        total_tickets = sum(getattr(p, 'tickets', 0) for p in ready_queue)
        if total_tickets == 0:
            return None

        winning_ticket = random.randint(1, total_tickets)
        winner = None
        ticket_count = 0
        for p in ready_queue:
            ticket_count += getattr(p, 'tickets', 0)
            if winning_ticket <= ticket_count:
                winner = p
                break
        
        if not winner:
            return None

        if not hasattr(winner, 'response_time') or winner.response_time == -1:
            winner.response_time = current_time - winner.arrival_time

        winner.update_remaining_time(1)
        completed = winner.get_remaining_time() == 0
        
        if completed:
            if not hasattr(winner, 'turnaround_time'):
                winner.turnaround_time = 0
            winner.turnaround_time = (current_time + 1) - winner.arrival_time
            winner.waiting_time = winner.turnaround_time - winner.burst_time
        
        return (winner, current_time, 1, completed)

    def run(self):
        if self.semilla is not None:
            random.seed(self.semilla)

        current_time = 0
        future_processes = sorted(self.procesos, key=lambda p: p.arrival_time)
        ready_queue = []
        
        while future_processes or any(p.get_remaining_time() > 0 for p in self.procesos):
            while future_processes and future_processes[0].arrival_time <= current_time:
                ready_queue.append(future_processes.pop(0))
            
            result = self._execute_tick(ready_queue, current_time)
            
            if result:
                proc, start, _, completed = result
                print(f" {start}-{start+1}: {proc.name} ejecutado. (Completado: {completed})")
                if completed:
                    ready_queue.remove(proc)
            
            current_time += 1
        
        self.display_final_metrics()

    #tabla de resultados.
    def display_final_metrics(self):
        """Display final scheduling metrics"""
        print(f"\n=== Final Results ===")
        
        completed_processes = [p for p in self.procesos if p.get_remaining_time() == 0]
        
        if not completed_processes:
            print("No processes completed!")
            return
        
        print(f"{'Process':<12} {'Burst':<6} {'Wait':<6} {'Turnaround':<10} {'Response':<8}")
        print("-" * 50)
        
        total_waiting = 0
        total_turnaround = 0
        total_response = 0
        
        for process in completed_processes:
            wait_time = getattr(process, 'waiting_time', 0)
            turnaround_time = getattr(process, 'turnaround_time', 0)
            response_time = getattr(process, 'response_time', 0)

            print(f"{process.name:<12} {process.burst_time:<6} {wait_time:<6} "
                  f"{turnaround_time:<10} {response_time:<8}")
            
            total_waiting += wait_time
            total_turnaround += turnaround_time
            total_response += response_time
        
        n = len(completed_processes)
        print("-" * 50)
        print(f"Average:       {'':<6} {total_waiting/n:<6.1f} "
              f"{total_turnaround/n:<10.1f} {total_response/n:<8.1f}")