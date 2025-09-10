from models.mlfq import MultilevelFeedbackQueue
from models.queue import Queue
from utils.get_data import GetData as gd

print('aprendan python ya')
process = gd.get_data()
print(f'Process data: {process['algoritmos'][3]['parametros']['colas']}')
queues_data = process['algoritmos'][3]
for queue_data in queues_data:
  print(f'Queue: {queue_data}')
  queue = Queue(queue_data['parametros']['colas']['nombre'],queues_data['procesos'], quantum=queue_data['parametros']['colas'].get('quantum'))
