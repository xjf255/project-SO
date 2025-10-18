import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import random
import heapq
from typing import List, Tuple, Dict, Any, Optional

# --- PASO 1: Importaciones para el gráfico ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ==============================================================================
# 1. CLASE DE PROCESO UNIVERSAL Y ALGORITMOS DE COLA
# ==============================================================================

class Process:
    """Clase base universal para un proceso, compatible con todos los algoritmos."""
    def __init__(self, pid: Any, burst_time: int, arrival_time: int, priority: int = 0, tickets: int = 0):
        self.pid = pid; self.name = str(pid); self.burst_time = burst_time; self.arrival_time = arrival_time
        self.priority = priority; self.tickets = tickets; self.reset()
    def reset(self):
        self.remaining_time = self.burst_time; self.response_time = -1; self.waiting_time = 0
        self.turnaround_time = 0; self.finish_time = -1
    def __repr__(self): return f"Process(pid={self.pid})"

class FirstComeFirstServedAlgorithm:
    def execute_processes(self, processes: List[Process], current_time: int) -> List[Tuple[Process, int, int, bool]]:
        if not processes: return []
        process = min(processes, key=lambda p: p.arrival_time)
        start_time = max(current_time, process.arrival_time)
        if process.response_time == -1: process.response_time = start_time - process.arrival_time
        exec_time = process.remaining_time; process.remaining_time = 0
        process.finish_time = start_time + exec_time
        process.turnaround_time = process.finish_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
        return [(process, start_time, exec_time, True)]

class RoundRobin:
    def __init__(self, quantum: int): self.quantum = quantum
    def execute_processes(self, processes: List[Process], current_time: int) -> List[Tuple[Process, int, int, bool]]:
        if not processes: return []
        process = min(processes, key=lambda p: p.arrival_time)
        start_time = max(current_time, process.arrival_time)
        if process.response_time == -1: process.response_time = start_time - process.arrival_time
        exec_time = min(self.quantum, process.remaining_time); process.remaining_time -= exec_time
        completed = process.remaining_time == 0
        if completed:
            process.finish_time = start_time + exec_time
            process.turnaround_time = process.finish_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
        return [(process, start_time, exec_time, completed)]

# ==============================================================================
# 2. LÓGICA DE LOS 5 PLANIFICADORES PRINCIPALES (MODIFICADOS PARA GANTT)
# ==============================================================================

class Queue:
    def __init__(self, name: str, priority: int, quantum: Optional[int] = None):
        self.name = name; self.priority = priority; self.quantum = quantum; self.processes: List[Process] = []
        self.scheduling_algorithm = RoundRobin(quantum) if quantum else FirstComeFirstServedAlgorithm()
    def add_process(self, process: Process): self.processes.append(process)
    def remove_process(self, process: Process):
        if process in self.processes: self.processes.remove(process)
    def has_ready_processes(self, current_time: int) -> bool:
        return any(p.remaining_time > 0 and p.arrival_time <= current_time for p in self.processes)
    def execute(self, current_time: int) -> List[Tuple[Process, int, int, bool]]:
        ready = [p for p in self.processes if p.remaining_time > 0 and p.arrival_time <= current_time]
        return self.scheduling_algorithm.execute_processes(ready, current_time)

class SJF_Scheduler:
    def run(self, config: Dict) -> Dict:
        processes = [Process(p['pid'], p['rafaga'], p.get('llegada', 0)) for p in config.get('procesos', [])]
        timeline, final_data, gantt_data, current_time = [], [], [], 0
        remaining_procs = processes.copy()
        while remaining_procs:
            ready_procs = [p for p in remaining_procs if p.arrival_time <= current_time]
            if not ready_procs: current_time = min(p.arrival_time for p in remaining_procs); continue
            next_proc = sorted(ready_procs, key=lambda p: (p.burst_time, p.arrival_time))[0]
            start_time = current_time
            next_proc.finish_time = start_time + next_proc.burst_time; next_proc.response_time = start_time - next_proc.arrival_time
            next_proc.turnaround_time = next_proc.finish_time - next_proc.arrival_time; next_proc.waiting_time = next_proc.turnaround_time - next_proc.burst_time
            timeline.append(f"{start_time}-{next_proc.finish_time}: {next_proc.pid} ejecutado.")
            gantt_data.append({'pid': next_proc.pid, 'start': start_time, 'duration': next_proc.burst_time})
            current_time = next_proc.finish_time
            final_data.append({"pid": next_proc.pid, "rafaga": next_proc.burst_time, "llegada": next_proc.arrival_time, "final": next_proc.finish_time, "tiempo_retorno": next_proc.turnaround_time, "tiempo_espera": next_proc.waiting_time, "tiempo_respuesta": next_proc.response_time})
            remaining_procs.remove(next_proc)
        return {"orden_ejecucion": timeline, "procesos_finales": sorted(final_data, key=lambda x: x['pid']), "gantt_data": gantt_data}

class FCFS_Scheduler:
    def run(self, config: Dict) -> Dict:
        processes = [Process(p['pid'], p['rafaga'], p.get('llegada', 0)) for p in config['procesos']]
        processes.sort(key=lambda p: p.arrival_time)
        timeline, final_data, gantt_data, current_time = [], [], [], 0
        for p in processes:
            start_time = max(current_time, p.arrival_time)
            p.finish_time = start_time + p.burst_time; p.response_time = start_time - p.arrival_time
            p.turnaround_time = p.finish_time - p.arrival_time; p.waiting_time = p.turnaround_time - p.burst_time
            timeline.append(f"{start_time}-{p.finish_time}: {p.pid} ejecutado.")
            gantt_data.append({'pid': p.pid, 'start': start_time, 'duration': p.burst_time})
            current_time = p.finish_time
            final_data.append({"pid": p.pid, "rafaga": p.burst_time, "llegada": p.arrival_time, "final": p.finish_time, "tiempo_retorno": p.turnaround_time, "tiempo_espera": p.waiting_time, "tiempo_respuesta": p.response_time})
        return {"orden_ejecucion": timeline, "procesos_finales": final_data, "gantt_data": gantt_data}

class LotteryScheduler:
    def run(self, config: Dict) -> Dict:
        semilla = config.get('parametros', {}).get('semilla')
        if semilla is not None: random.seed(semilla)
        procesos = [Process(p['pid'], p['rafaga'], p.get('llegada', 0), tickets=p.get('boletos', 1)) for p in config.get('procesos', [])]
        log, gantt_data, current_time = [], [], 0
        future = sorted(procesos, key=lambda p: p.arrival_time)
        ready = []
        while future or any(p.remaining_time > 0 for p in procesos):
            while future and future[0].arrival_time <= current_time: ready.append(future.pop(0))
            if not ready: current_time = future[0].arrival_time if future else current_time + 1; continue
            total_tickets = sum(p.tickets for p in ready);
            if total_tickets == 0: total_tickets = len(ready)
            winning_ticket = random.randint(1, total_tickets)
            winner, ticket_count = None, 0
            for p in ready:
                ticket_count += p.tickets if p.tickets > 0 else 1
                if winning_ticket <= ticket_count: winner = p; break
            if winner:
                if winner.response_time == -1: winner.response_time = current_time - winner.arrival_time
                gantt_data.append({'pid': winner.pid, 'start': current_time, 'duration': 1})
                winner.remaining_time -= 1
                msg = f"{current_time}-{current_time+1}: {winner.pid} ejecutado."
                if winner.remaining_time == 0:
                    winner.finish_time = current_time + 1; winner.turnaround_time = winner.finish_time - winner.arrival_time
                    winner.waiting_time = winner.turnaround_time - winner.burst_time; ready.remove(winner); msg += " (Completado)"
                log.append(msg)
            current_time += 1
        final_data = [{"pid": p.pid, "rafaga": p.burst_time, "llegada": p.arrival_time, "final": p.finish_time, "tiempo_retorno": p.turnaround_time, "tiempo_espera": p.waiting_time, "tiempo_respuesta": p.response_time} for p in procesos]
        return {"orden_ejecucion": log, "procesos_finales": final_data, "gantt_data": gantt_data}

class PriorityScheduler:
    def run(self, config: Dict) -> Dict:
        params = config.get("parametros", {})
        # --- LÓGICA REACTIVADA ---
        order_asc = params.get("orden_prioridad", "menor_numero_mayor_prioridad") == "menor_numero_mayor_prioridad"
        
        procs = [Process(p["pid"], p["rafaga"], p.get("llegada", 0), p["prioridad"]) for p in config["procesos"]]
        time, completed, n = 0, 0, len(procs)
        heap, log, gantt_data = [], [], []
        procs.sort(key=lambda p: p.arrival_time)
        proc_idx = 0
        
        while completed < n:
            while proc_idx < n and procs[proc_idx].arrival_time <= time:
                p = procs[proc_idx]
                # Usa la prioridad directamente o su negativo para ordenar
                priority_val = p.priority if order_asc else -p.priority
                heapq.heappush(heap, (priority_val, p.arrival_time, p.pid, p))
                proc_idx += 1
            
            if not heap:
                time = procs[proc_idx].arrival_time if proc_idx < n else time + 1
                continue
            
            _, _, _, current_proc = heapq.heappop(heap)
            
            if current_proc.response_time == -1: current_proc.response_time = time - current_proc.arrival_time
            
            log.append(f"{time}-{time+1}: {current_proc.pid} ejecutado.")
            gantt_data.append({'pid': current_proc.pid, 'start': time, 'duration': 1})
            
            current_proc.remaining_time -= 1
            time += 1
            
            if current_proc.remaining_time == 0:
                current_proc.finish_time = time
                current_proc.turnaround_time = current_proc.finish_time - current_proc.arrival_time
                current_proc.waiting_time = current_proc.turnaround_time - current_proc.burst_time
                completed += 1
            else:
                # Vuelve a insertar el proceso en el montículo con la misma lógica de prioridad
                priority_val = current_proc.priority if order_asc else -current_proc.priority
                heapq.heappush(heap, (priority_val, current_proc.arrival_time, current_proc.pid, current_proc))
                
        final_data = [{"pid": p.pid, "rafaga": p.burst_time, "llegada": p.arrival_time, "final": p.finish_time, "tiempo_retorno": p.turnaround_time, "tiempo_espera": p.waiting_time, "tiempo_respuesta": p.response_time} for p in procs]
        return {"orden_ejecucion": log, "procesos_finales": final_data, "gantt_data": gantt_data}

class MLFQScheduler:
    def run(self, config: Dict) -> Dict:
        all_processes = [Process(p['pid'], p['rafaga'], p.get('llegada', 0)) for p in config.get('procesos', [])]
        queues_data = config.get('parametros', {}).get('colas', [])
        queues = [Queue(qc['nombre'], idx + 1, qc.get('quantum')) for idx, qc in enumerate(queues_data)]
        log, gantt_data, current_time = [], [], 0
        if queues:
            for p in all_processes: queues[0].add_process(p)
        while any(p.remaining_time > 0 for p in all_processes):
            executed_in_tick = False
            for queue_idx, queue in enumerate(queues):
                if queue.has_ready_processes(current_time):
                    results = queue.execute(current_time)
                    if results:
                        process, start_time, duration, completed = results[0]
                        gantt_data.append({'pid': process.pid, 'start': start_time, 'duration': duration})
                        current_time = start_time
                        for _ in range(duration): log.append(f"{current_time}-{current_time+1}: {process.pid} (desde {queue.name})"); current_time += 1
                        if not completed and queue.quantum and duration == queue.quantum:
                            if queue_idx < len(queues) - 1:
                                queue.remove_process(process); queues[queue_idx + 1].add_process(process)
                                log.append(f"-> {process.pid} degradado a {queues[queue_idx + 1].name}")
                        executed_in_tick = True; break 
            if not executed_in_tick:
                future_arrivals = [p.arrival_time for p in all_processes if p.arrival_time > current_time and p.remaining_time > 0]
                current_time = min(future_arrivals) if future_arrivals else current_time + 1
        final_data = [{"pid": p.pid, "rafaga": p.burst_time, "llegada": p.arrival_time, "final": p.finish_time, "tiempo_retorno": p.turnaround_time, "tiempo_espera": p.waiting_time, "tiempo_respuesta": p.response_time} for p in all_processes]
        return {"orden_ejecucion": log, "procesos_finales": final_data, "gantt_data": gantt_data}


# ==============================================================================
# 4. CLASE PRINCIPAL DE LA INTERFAZ GRÁFICA (GUI)
# ==============================================================================

class SchedulerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Simulador de Planificación de CPU"); master.geometry("1440x850")
        self.algorithms = {"SJF": SJF_Scheduler(), "FCFS": FCFS_Scheduler(), "Loteria": LotteryScheduler(), "Prioridades": PriorityScheduler(), "FeedbackQueue": MLFQScheduler()}
        self.loaded_data = {}
        self.setup_styles()
        self.create_widgets()
        self.update_ui_for_algorithm()

    def setup_styles(self):
        self.COLOR_BACKGROUND = "#2b2b2b"; self.COLOR_FRAME = "#3c3f41"; self.COLOR_TEXT = "#bbbbbb"
        self.COLOR_ACCENT = "#007acc"; self.COLOR_ACCENT_TEXT = "#ffffff"; self.COLOR_ENTRY_BG = "#45494a"
        self.COLOR_HEADER = "#323232"
        self.style = ttk.Style(self.master); self.style.theme_use("clam")
        self.master.configure(bg=self.COLOR_BACKGROUND)
        self.style.configure(".", background=self.COLOR_BACKGROUND, foreground=self.COLOR_TEXT, fieldbackground=self.COLOR_ENTRY_BG, borderwidth=1)
        self.style.configure("TFrame", background=self.COLOR_BACKGROUND)
        self.style.configure("TLabel", background=self.COLOR_BACKGROUND, foreground=self.COLOR_TEXT, padding=5, font=('Segoe UI', 10))
        self.style.configure("TLabelFrame", background=self.COLOR_BACKGROUND, bordercolor=self.COLOR_FRAME, relief="solid", padding=10)
        self.style.configure("TLabelFrame.Label", background=self.COLOR_BACKGROUND, foreground=self.COLOR_TEXT, font=('Segoe UI', 11, 'bold'))
        self.style.configure("TRadiobutton", background=self.COLOR_BACKGROUND, foreground=self.COLOR_TEXT, indicatorbackground=self.COLOR_FRAME, font=('Segoe UI', 10))
        self.style.map("TRadiobutton", indicatorcolor=[('selected', self.COLOR_ACCENT)])
        self.style.configure("TButton", background=self.COLOR_ACCENT, foreground=self.COLOR_ACCENT_TEXT, padding=5, font=('Segoe UI', 10, 'bold'), borderwidth=0)
        self.style.map("TButton", background=[('active', '#005a9e')])
        self.style.configure("Treeview", background=self.COLOR_FRAME, fieldbackground=self.COLOR_FRAME, foreground=self.COLOR_TEXT, rowheight=25)
        self.style.configure("Treeview.Heading", background=self.COLOR_HEADER, foreground=self.COLOR_ACCENT_TEXT, font=('Segoe UI', 10, 'bold'), relief="flat")
        self.style.map("Treeview.Heading", background=[('active', self.COLOR_ACCENT)])
        self.style.configure("TNotebook", background=self.COLOR_BACKGROUND, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.COLOR_FRAME, foreground=self.COLOR_TEXT, padding=[10, 5], font=('Segoe UI', 10, 'bold'))
        self.style.map("TNotebook.Tab", background=[("selected", self.COLOR_ACCENT)], foreground=[("selected", self.COLOR_ACCENT_TEXT)])

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="15"); main_frame.pack(fill=tk.BOTH, expand=True)
        left_column = ttk.Frame(main_frame, width=400); left_column.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15)); left_column.pack_propagate(False)
        right_column = ttk.Frame(main_frame); right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        file_frame = ttk.LabelFrame(left_column, text="1. Cargar Datos"); file_frame.pack(fill=tk.X, pady=5)
        ttk.Button(file_frame, text="Cargar Archivo de Configuración", command=self.load_file).pack(fill=tk.X)
        self.algo_frame = ttk.LabelFrame(left_column, text="2. Algoritmo"); self.algo_frame.pack(fill=tk.X, pady=5)
        self.selected_algorithm = tk.StringVar(); self.selected_algorithm.trace("w", self.update_ui_for_algorithm)
        
        self.mlfq_config_frame = ttk.LabelFrame(left_column, text="Configuración Colas")
        self.mlfq_tree = ttk.Treeview(self.mlfq_config_frame, columns=("Nombre", "Prio", "Quantum"), show="headings", height=3)
        for col in ("Nombre", "Prio", "Quantum"): self.mlfq_tree.heading(col, text=col); self.mlfq_tree.column(col, width=70)
        self.mlfq_tree.pack(fill=tk.X, pady=5)
        
        self.config_frame = ttk.LabelFrame(left_column, text="3. Parámetros")
        self.seed_label = ttk.Label(self.config_frame, text="Semilla (Loteria):"); self.seed_entry = ttk.Entry(self.config_frame, width=15)
        
        # --- (REACTIVADO) Menú desplegable para Prioridades ---
        self.priority_order_label = ttk.Label(self.config_frame, text="Orden Prioridad:")
        self.priority_order_var = tk.StringVar()
        self.priority_order_menu = ttk.OptionMenu(
            self.config_frame, self.priority_order_var, "", 
            "menor_numero_mayor_prioridad", "mayor_numero_mayor_prioridad", style="TButton"
        )

        control_frame = ttk.Frame(left_column); control_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20)
        ttk.Button(control_frame, text="Ejecutar Simulación", command=self.run_simulation, padding=10).pack(fill=tk.X)
        ttk.Button(control_frame, text="Limpiar Todo", command=self.clear_all, padding=10).pack(fill=tk.X, pady=5)

        notebook = ttk.Notebook(right_column)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        tab_gantt = ttk.Frame(notebook); notebook.add(tab_gantt, text='Gráfico de Gantt')
        tab_log = ttk.Frame(notebook); notebook.add(tab_log, text='Traza de Ejecución')
        tab_metrics = ttk.Frame(notebook); notebook.add(tab_metrics, text='Tabla de Métricas')

        self.gantt_frame = ttk.Frame(tab_gantt); self.gantt_frame.pack(fill=tk.BOTH, expand=True)
        self.fig = Figure(figsize=(10, 5), dpi=100, facecolor=self.COLOR_BACKGROUND)
        self.gantt_canvas = FigureCanvasTkAgg(self.fig, master=self.gantt_frame)
        self.gantt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(tab_log, state="disabled", wrap=tk.WORD, bg=self.COLOR_FRAME, fg=self.COLOR_TEXT, relief="solid", bd=1, selectbackground=self.COLOR_ACCENT, insertbackground=self.COLOR_ACCENT_TEXT)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.results_tree = ttk.Treeview(tab_metrics, columns=("PID", "Ráfaga", "Llegada", "Final", "T. Retorno", "T. Espera", "T. Respuesta"), show="headings")
        for col in self.results_tree['columns']: self.results_tree.heading(col, text=col); self.results_tree.column(col, width=120, anchor=tk.CENTER)
        self.results_tree.pack(fill=tk.BOTH, expand=True)

    def draw_gantt_chart(self, gantt_data):
        self.fig.clear()
        if not gantt_data: self.gantt_canvas.draw(); return

        ax = self.fig.add_subplot(111)
        pids = sorted(list(set(d['pid'] for d in gantt_data)), reverse=True)
        y_pos = {pid: i for i, pid in enumerate(pids)}
        
        for item in gantt_data:
            ax.broken_barh([(item['start'], item['duration'])], (y_pos[item['pid']] - 0.4, 0.8), facecolors=self.COLOR_ACCENT)

        ax.set_yticks([i for i in range(len(pids))])
        ax.set_yticklabels(pids, color=self.COLOR_TEXT)
        ax.set_xlabel('Tiempo', color=self.COLOR_TEXT)
        ax.set_ylabel('Procesos', color=self.COLOR_TEXT)
        ax.set_title('Diagrama de Gantt', color=self.COLOR_ACCENT_TEXT, fontsize=14, weight='bold')
        ax.grid(True, axis='x', linestyle='--', color=self.COLOR_FRAME)
        
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(self.COLOR_FRAME); ax.spines['left'].set_color(self.COLOR_FRAME)
        ax.tick_params(axis='x', colors=self.COLOR_TEXT); ax.tick_params(axis='y', colors=self.COLOR_TEXT)
        ax.set_facecolor(self.COLOR_BACKGROUND)

        self.fig.tight_layout()
        self.gantt_canvas.draw()
    
    def load_file(self):
        filepath = filedialog.askopenfilename(title="Seleccionar archivo JSON", filetypes=[("JSON files", "*.json")])
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: self.loaded_data = json.load(f)
            self.populate_gui_from_data()
            messagebox.showinfo("Éxito", "Archivo de configuración cargado.")
        except Exception as e: messagebox.showerror("Error de Carga", f"No se pudo cargar el archivo:\n{e}")
    
    def populate_gui_from_data(self):
        self.clear_all(clear_file_data=False)
        for widget in self.algo_frame.winfo_children(): widget.destroy()
        alg_names = [alg['algoritmo'] for alg in self.loaded_data.get('algoritmos', [])]
        if not alg_names: return
        for name in alg_names: ttk.Radiobutton(self.algo_frame, text=name, variable=self.selected_algorithm, value=name).pack(anchor=tk.W)
        self.selected_algorithm.set(alg_names[0])
    
    def update_ui_for_algorithm(self, *args):
        algo_name = self.selected_algorithm.get()
        if not algo_name: return
        
        self.config_frame.pack_forget(); self.mlfq_config_frame.pack_forget()
        for w in [self.seed_label, self.seed_entry, self.priority_order_label, self.priority_order_menu]: 
            w.pack_forget()
        for i in self.mlfq_tree.get_children(): self.mlfq_tree.delete(i)

        config = next((item for item in self.loaded_data.get('algoritmos', []) if item['algoritmo'] == algo_name), None)
        if not config: return
        
        params = config.get('parametros', {})
        if algo_name == "Loteria":
            self.config_frame.pack(fill=tk.X, pady=5)
            self.seed_label.pack(side=tk.LEFT, anchor='w')
            self.seed_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.seed_entry.delete(0, tk.END); self.seed_entry.insert(0, params.get('semilla', ''))
        elif algo_name == "Prioridades":
            self.config_frame.pack(fill=tk.X, pady=5)
            self.priority_order_label.pack(anchor=tk.W)
            self.priority_order_menu.pack(fill=tk.X)
            self.priority_order_var.set(params.get('orden_prioridad', 'menor_numero_mayor_prioridad'))
        elif algo_name == "FeedbackQueue":
            self.mlfq_config_frame.pack(fill=tk.X, pady=5)
            for idx, q in enumerate(params.get('colas', [])):
                self.mlfq_tree.insert("", "end", values=(q.get('nombre'), idx + 1, q.get('quantum', 'FCFS')))

    def run_simulation(self):
        self.log_text.config(state="normal"); self.log_text.delete("1.0", tk.END)
        for i in self.results_tree.get_children(): self.results_tree.delete(i)
        
        algo_name = self.selected_algorithm.get()
        if not algo_name: messagebox.showerror("Error", "Ningún algoritmo seleccionado."); return
        
        runner = self.algorithms.get(algo_name)
        if not runner: messagebox.showerror("Error", f"Algoritmo '{algo_name}' no implementado."); return
        
        config = next((item for item in self.loaded_data.get('algoritmos', []) if item['algoritmo'] == algo_name), None)
        if not config: messagebox.showerror("Error", "No se encontró la configuración para el algoritmo."); return
        
        # --- (AÑADIDO) Actualiza la configuración de prioridad desde la UI antes de ejecutar ---
        if algo_name == "Prioridades":
            if 'parametros' not in config: config['parametros'] = {}
            config['parametros']['orden_prioridad'] = self.priority_order_var.get()
        
        try:
            results = runner.run(config)
            if results:
                for line in results["orden_ejecucion"]: self.log_text.insert(tk.END, line + "\n")
                
                sorted_processes = sorted(results["procesos_finales"], key=lambda p: p['pid'])
                for p in sorted_processes:
                    values = (
                        p.get("pid"), p.get("rafaga"), p.get("llegada"), 
                        f"{p.get('final', '-'):.0f}" if isinstance(p.get('final'), (int, float)) else "-",
                        f"{p.get('tiempo_retorno', '-'):.2f}" if isinstance(p.get('tiempo_retorno'), (int, float)) else "-",
                        f"{p.get('tiempo_espera', '-'):.2f}" if isinstance(p.get('tiempo_espera'), (int, float)) else "-",
                        f"{p.get('tiempo_respuesta', '-'):.2f}" if isinstance(p.get('tiempo_respuesta'), (int, float)) else "-"
                    )
                    self.results_tree.insert("", "end", values=values)
                    
                self.draw_gantt_chart(results.get("gantt_data", []))
        except Exception as e: messagebox.showerror("Error en Simulación", f"Ocurrió un error: {e}")
        finally: self.log_text.config(state="disabled")

    def clear_all(self, clear_file_data=True):
        if clear_file_data: self.loaded_data = {}
        for i in self.mlfq_tree.get_children(): self.mlfq_tree.delete(i)
        self.log_text.config(state="normal"); self.log_text.delete("1.0", tk.END); self.log_text.config(state="disabled")
        for i in self.results_tree.get_children(): self.results_tree.delete(i)
        for widget in self.algo_frame.winfo_children(): widget.destroy()
        self.fig.clear()
        self.gantt_canvas.draw()

# ==============================================================================
# 5. PUNTO DE ENTRADA DE LA APLICACIÓN
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerGUI(root)
    root.mainloop()