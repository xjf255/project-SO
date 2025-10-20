from models.mlfq import MultilevelFeedbackQueue
from models.queue import Queue
from models.process import Process
from utils.get_data import get_data
from models.lottery_scheduler import LotteryScheduler
from models.priority import priorityPreemptivo

import sys
import os

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

data = get_data()
print(f'Process data: {data['algoritmos'][3]['parametros']['colas']}')
queues_data = data['algoritmos'][3]

queue_processes_data = queues_data['procesos']
processes = []
queues = []

for process_data in queue_processes_data:
  process = Process(process_data['pid'], process_data['rafaga'], process_data.get('llegada', 0))
  processes.append(process)

for queue_data in queues_data['parametros']['colas']:
  print(f'Queue: {queue_data}')
  queue = Queue(queue_data.get('nombre'), quantum=queue_data.get('quantum') if 'quantum' in queue_data else None)
  queues.append(queue)

mlfq = MultilevelFeedbackQueue(*queues)
mlfq.load_processes(processes)
mlfq.run()


# --- CÓDIGO PARA LOTTERY SCHEDULER ---
print(f"\n============================")
print(f"Algoritmo de Loteria")

config_loteria = None
for alg_config in data['algoritmos']:
    if alg_config['algoritmo'] == 'Loteria':
        config_loteria = alg_config
        break

if config_loteria:
    scheduler = LotteryScheduler(config_loteria)
    scheduler.run()
    #aqui termina el de loteria

# -- ALGORITMO DE PRIORIDADES --
print(f"\n============================")
print(f"Algoritmo de Prioridades (preventivo)")

#Aqui solo hacemos que del objeto DATA agarremos los datos del proceso 'Prioridades'
config_priority = None
for alg_config in data['algoritmos']:
   if alg_config['algoritmo'].lower() == 'prioridades':
      config_priority = alg_config
      break
   
#Si se encuentra se ejecuta el algoritmo de Prioridades, sino no ÑLAKSJFLAKJF
if config_priority:
   resultado = priorityPreemptivo(config_priority)
   #Solo para mostrar los resultados en consola
   print("Orden de ejecucion (TimeLine):")
   print(" -> ".join(resultado["orden_ejecucion"]))
   print("\n Detalle de procesos:")
   for p in resultado["procesos"]:
      print(
         f"{p['pid']}: llegada={p['llegada']}, rafaga={p['rafaga']}, prioridad={p['prioridad']},"
         f"inicio={p['inicio']}, final={p['final']}, espera={p['tiempo_espera']}, retorno={p['tiempo_retorno']}"
      )
else:
   print("No se encontraron procesos para ejecutar 'Prioridades'")
#Fin de algoritmo de prioridades

# --- ALGORITMO SJF ---
from models.sjf import run_sjf

print(f"\n============================")
print(f"Algoritmo SJF (Shortest Job First)")

config_sjf = None
for alg_config in data['algoritmos']:
    if alg_config['algoritmo'].lower() == 'sjf':
        config_sjf = alg_config
        break

if config_sjf:
    run_sjf(config_sjf)
else:
    print("No se encontraron procesos para ejecutar 'SJF'")
