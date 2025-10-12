import heapq

class Priority:
    def __init__(self,pid,llegada,rafaga,prioridad):
        self.pid = pid
        self.llegada = llegada
        self.rafaga = rafaga
        self.prioridad = prioridad
        self.restante = rafaga #Para que no de problema en el FRONTEND. Igual se usa en el bucle de ejecucion de los procesos
        self.inicio = None
        self.final = None

    def __repr__(self):
        return f"{self.pid}(Llegada:{self.llegada}, Ráfaga:{self.rafaga}, Prioridad:{self.prioridad})"
    
def priorityPreemptivo(data):
    #Obtenemos los datos del JSON
    processesData = data["procesos"]
    parameters = data["parametros"]

    priorityOrder = parameters["orden_prioridad"] == "menor_numero_mayor_prioridad"
    tieCriterion = parameters["criterio_empate"]

    #Le damos la estructura del objeto 'processes'
    processes = [Priority(p["pid"], p["llegada"], p["rafaga"], p["prioridad"]) for p in processesData]

    #Iniciamos variables para llevar control del estado de los procesos
    time = 0
    completed = 0
    n = len(processes)
    heap = []
    timeline = [] #para llevar el orden de ejecucion de los procesos

    #Ordenamos los procesos de manera ascendente segun su tiempo de llegada e iniciamos otras variables
    processes.sort(key=lambda p: p.llegada)
    i = 0
    actual = None

    while completed < n:
        while i<n and processes[i].llegada <= time:
            priorityVal = processes[i].prioridad if priorityOrder else -processes[i].prioridad
            heapq.heappush(heap, (priorityVal, processes[i].llegada, processes[i]))
            i += 1
        
        if not heap:
            time += 1
            continue
        
        #Se toma el proceso de mayor prioridad (el prioridad menor)
        _, _, actual = heapq.heappop(heap)

        #Si se ejecuta por primera vez se guarda el tiempo en que se ejecutó
        if actual.inicio is None:
            actual.inicio = time
        
        #Ejecutamos un ciclo de tiempo de CPU (1 unidad de tiempo)
        timeline.append(actual.pid)
        actual.restante -= 1
        time += 1

        #Si se terminó de ejecutar
        if actual.restante == 0:
            actual.final = time
            completed += 1
        else:
            #si es que no se termina
            priorityVal = actual.prioridad if priorityOrder else -actual.prioridad
            heapq.heappush(heap, (priorityVal, actual.llegada, actual))

    #supongo que esto les puede ayudar para realizar el FRONTEND
    return {
        "orden_ejecucion": timeline,
        "procesos": [
            {
                "pid": p.pid,
                "llegada": p.llegada,
                "rafaga": p.rafaga,
                "prioridad": p.prioridad,
                "inicio": p.inicio,
                "final": p.final,
                "tiempo_espera": p.final - p.llegada - p.rafaga,
                "tiempo_retorno": p.final - p.llegada
            } for p in processes
        ]
    }