# 📁 models/sjf.py

class Proceso:
    def __init__(self, pid, llegada, rafaga):
        self.pid = pid
        self.llegada = llegada
        self.rafaga = rafaga
        self.finalizacion = 0
        self.retorno = 0
        self.espera = 0
        self.inicio = 0
        self.completado = False


def algoritmo_sjf(procesos):
    tiempo = 0
    completados = 0
    n = len(procesos)
    orden_ejecucion = []

    print("\n--- INICIO DE SIMULACIÓN SJF ---\n")

    while completados < n:
        disponibles = [p for p in procesos if p.llegada <= tiempo and not p.completado]

        if not disponibles:
            print(f"Tiempo {tiempo}: CPU en espera (no hay procesos disponibles)")
            tiempo += 1
            continue

        actual = min(disponibles, key=lambda x: x.rafaga)
        actual.inicio = tiempo
        print(f"Tiempo {tiempo}: Ejecutando {actual.pid} (ráfaga = {actual.rafaga})")

        tiempo += actual.rafaga
        actual.finalizacion = tiempo
        actual.retorno = actual.finalizacion - actual.llegada
        actual.espera = actual.retorno - actual.rafaga
        actual.completado = True
        completados += 1
        orden_ejecucion.append(actual.pid)

        print(f" -> {actual.pid} finaliza en tiempo {actual.finalizacion}\n")

    print("\n--- FIN DE SIMULACIÓN SJF ---\n")

    return {
        "orden_ejecucion": orden_ejecucion,
        "procesos": procesos
    }


def run_sjf(config_sjf):
    # Extraer los procesos desde la configuración del JSON
    procesos_data = config_sjf['procesos']
    procesos = []

    for p in procesos_data:
        procesos.append(Proceso(p['pid'], p.get('llegada', 0), p['rafaga']))

    resultado = algoritmo_sjf(procesos)

    print("Orden de ejecución (Timeline):")
    print(" -> ".join(resultado["orden_ejecucion"]))

    print("\nDetalle de procesos:")
    print("------------------------------------------------------------")
    print("Proceso | Llegada | Ráfaga | Inicio | Final | Espera | Retorno")
    print("------------------------------------------------------------")
    for p in resultado["procesos"]:
        print(f"{p.pid:^8} | {p.llegada:^7} | {p.rafaga:^6} | {p.inicio:^6} | {p.finalizacion:^6} | {p.espera:^6} | {p.retorno:^7}")
    print("------------------------------------------------------------")
