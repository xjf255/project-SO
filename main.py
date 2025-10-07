from models.mlfq import MultilevelFeedbackQueue
from models.queue import Queue
from models.process import Process
from utils.get_data import get_data
from models.lottery_scheduler import LotteryScheduler


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
    