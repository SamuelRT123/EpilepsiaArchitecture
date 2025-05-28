import datetime

class HistorialMedico:
    def __init__(self, epilepsia=False, medicacion=None, otros_diagnosticos=None):
        self.epilepsia = epilepsia
        self.medicacion = medicacion or []
        self.otros_diagnosticos = otros_diagnosticos or []

    @staticmethod
    def from_dict(d):
        return HistorialMedico(
            epilepsia=d.get("epilepsia", False),
            medicacion=d.get("medicacion", []),
            otros_diagnosticos=d.get("otros_diagnosticos", [])
        )


class Paciente:
    def __init__(self, id, nombre, edad, sexo, historial_medico):
        self.id = id
        self.nombre = nombre
        self.edad = edad
        self.sexo = sexo
        self.historial_medico = historial_medico

    @staticmethod
    def from_dict(d):
        return Paciente(
            id=d["id"],
            nombre=d["nombre"],
            edad=d["edad"],
            sexo=d["sexo"],
            historial_medico=HistorialMedico.from_dict(d.get("historial_medico", {}))
        )


class FiltrosAplicados:
    def __init__(self, notch, pasa_alto, pasa_bajo):
        self.notch = notch
        self.pasa_alto = pasa_alto
        self.pasa_bajo = pasa_bajo

    @staticmethod
    def from_dict(d):
        return FiltrosAplicados(
            notch=d.get("notch"),
            pasa_alto=d.get("pasa_alto"),
            pasa_bajo=d.get("pasa_bajo")
        )


class Examen:
    def __init__(self, id, fecha, duracion_segundos, frecuencia_muestreo, electrodos, sistema_colocacion, filtros_aplicados):
        self.id = id
        self.fecha = datetime.datetime.fromisoformat(fecha.replace("Z", "+00:00"))
        self.duracion_segundos = duracion_segundos
        self.frecuencia_muestreo = frecuencia_muestreo
        self.electrodos = electrodos
        self.sistema_colocacion = sistema_colocacion
        self.filtros_aplicados = filtros_aplicados

    @staticmethod
    def from_dict(d):
        return Examen(
            id=d["id"],
            fecha=d["fecha"],
            duracion_segundos=d["duracion_segundos"],
            frecuencia_muestreo=d["frecuencia_muestreo"],
            electrodos=d["electrodos"],
            sistema_colocacion=d["sistema_colocacion"],
            filtros_aplicados=FiltrosAplicados.from_dict(d.get("filtros_aplicados", {}))
        )


class Dato:
    def __init__(self, tiempo, valores):
        self.tiempo = tiempo
        self.valores = valores

    @staticmethod
    def from_dict(d):
        return Dato(
            tiempo=d["tiempo"],
            valores=d["valores"]
        )


class Evento:
    def __init__(self, tipo, canal=None, canales=None, tiempo=None, tiempo_inicio=None, tiempo_fin=None, amplitud=None, frecuencia_dominante=None, descripcion=None, nivel_ruido=None, frecuencia=None):
        self.tipo = tipo
        self.canal = canal
        self.canales = canales
        self.tiempo = tiempo
        self.tiempo_inicio = tiempo_inicio
        self.tiempo_fin = tiempo_fin
        self.amplitud = amplitud
        self.frecuencia_dominante = frecuencia_dominante
        self.descripcion = descripcion
        self.nivel_ruido = nivel_ruido
        self.frecuencia = frecuencia

    @staticmethod
    def from_dict(d):
        return Evento(
            tipo=d.get("tipo"),
            canal=d.get("canal"),
            canales=d.get("canales"),
            tiempo=d.get("tiempo"),
            tiempo_inicio=d.get("tiempo_inicio"),
            tiempo_fin=d.get("tiempo_fin"),
            amplitud=d.get("amplitud"),
            frecuencia_dominante=d.get("frecuencia_dominante"),
            descripcion=d.get("descripcion"),
            nivel_ruido=d.get("nivel_ruido"),
            frecuencia=d.get("frecuencia"),
        )


class EspectroFrecuencial:
    def __init__(self, delta, theta, alpha, beta, gamma):
        self.delta = delta
        self.theta = theta
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    @staticmethod
    def from_dict(d):
        return EspectroFrecuencial(
            delta=d.get("delta"),
            theta=d.get("theta"),
            alpha=d.get("alpha"),
            beta=d.get("beta"),
            gamma=d.get("gamma")
        )


class Analisis:
    def __init__(self, espectro_frecuencial, sincronizacion_canal):
        # espectro_frecuencial es un dict canal -> EspectroFrecuencial
        self.espectro_frecuencial = {k: EspectroFrecuencial.from_dict(v) for k, v in espectro_frecuencial.items()}
        self.sincronizacion_canal = sincronizacion_canal

    @staticmethod
    def from_dict(d):
        return Analisis(
            espectro_frecuencial=d.get("espectro_frecuencial", {}),
            sincronizacion_canal=d.get("sincronizacion_canal", {})
        )


class EEGRecord:
    def __init__(self, paciente, examen, datos, eventos, analisis):
        self.paciente = paciente
        self.examen = examen
        self.datos = datos
        self.eventos = eventos
        self.analisis = analisis

    def __str__(self):
        return f"Paciente: {self.paciente.nombre} ({self.paciente.id}), Examen: {self.examen.id} en {self.examen.fecha.isoformat()}"

    @staticmethod
    def from_dict(d):
        paciente = Paciente.from_dict(d["paciente"])
        examen = Examen.from_dict(d["examen"])
        datos = [Dato.from_dict(x) for x in d.get("datos", [])]
        eventos = [Evento.from_dict(x) for x in d.get("eventos", [])]
        analisis = Analisis.from_dict(d.get("analisis", {}))
        return EEGRecord(paciente, examen, datos, eventos, analisis)
