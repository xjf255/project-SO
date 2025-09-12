from models.mlfq import MultilevelFeedbackQueue
from models.queue import Queue
from models.process import Process
from utils.get_data import get_data

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
  queue = Queue(queue_data.get('nombre'), quantum=queue_data.get('quantum'))
  queues.append(queue)

mlfq = MultilevelFeedbackQueue(*queues)
mlfq.load_processes(processes)
mlfq.run()