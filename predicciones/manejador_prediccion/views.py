from django.shortcuts import render
from django.http import JsonResponse
import json

def detectar_anomalias(json_eeg):
    """
    Función para detectar anomalías en datos EEG
    """
    anomalias = []
    
    if "eventos" in json_eeg:
        for evento in json_eeg["eventos"]:
            tipo = evento.get("tipo", "desconocido")
            tiempo = evento.get("tiempo", evento.get("tiempo_inicio", "N/A"))
            descripcion = evento.get("descripcion", "")
            
            if tipo == "pico":
                mensaje = f"Pico detectado en {evento['canal']} en {tiempo}s con amplitud {evento['amplitud']} μV."
            elif tipo == "artefacto":
                mensaje = f"Artefacto en {evento['canal']} en {tiempo}s: {descripcion}."
            elif tipo == "epileptiforme":
                mensaje = f"Descarga epileptiforme en canales {', '.join(evento['canales'])} de {evento['tiempo_inicio']}s a {evento['tiempo_fin']}s."
            else:
                mensaje = f"Evento desconocido '{tipo}' en {tiempo}s."
            
            anomalias.append({
                'tipo': tipo,
                'mensaje': mensaje,
                'tiempo': tiempo,
                'severidad': obtener_severidad(tipo)
            })
    
    return anomalias

def obtener_severidad(tipo_evento):
    """
    Determina la severidad del evento detectado
    """
    severidades = {
        'epileptiforme': 'Alta',
        'pico': 'Media',
        'artefacto': 'Baja'
    }
    return severidades.get(tipo_evento, 'Desconocida')

def generar_prediccion(anomalias, datos_paciente):
    """
    Genera una predicción basada en las anomalías detectadas
    """
    total_anomalias = len(anomalias)
    anomalias_criticas = len([a for a in anomalias if a['severidad'] == 'Alta'])
    anomalias_medias = len([a for a in anomalias if a['severidad'] == 'Media'])
    
    # Lógica de predicción simple
    if anomalias_criticas > 0:
        riesgo = "Alto"
        recomendacion = "Se recomienda consulta inmediata con neurólogo especialista"
    elif anomalias_medias > 2:
        riesgo = "Medio"
        recomendacion = "Monitoreo continuo y seguimiento médico recomendado"
    elif total_anomalias > 0:
        riesgo = "Bajo"
        recomendacion = "Seguimiento de rutina, anomalías menores detectadas"
    else:
        riesgo = "Muy Bajo"
        recomendacion = "EEG normal, continúe con controles regulares"
    
    # Considerar historial médico del paciente
    if datos_paciente.get('historial_medico', {}).get('epilepsia'):
        if riesgo in ['Alto', 'Medio']:
            recomendacion += ". Paciente con historial de epilepsia - revisar medicación actual"
    
    return {
        'riesgo': riesgo,
        'total_anomalias': total_anomalias,
        'anomalias_criticas': anomalias_criticas,
        'recomendacion': recomendacion,
        'fecha_analisis': '2025-05-29'
    }

def obtener_datos_examen():
    """
    Datos del examen EEG (normalmente vendrían de base de datos)
    """
    return {
        "paciente": {
            "id": "12345",
            "nombre": "Juan Pérez",
            "edad": 30,
            "sexo": "M",
            "historial_medico": {
                "epilepsia": True,
                "medicacion": ["levetiracetam"],
                "otros_diagnosticos": ["migraña"]
            }
        },
        "examen": {
            "id": "EEG20250403-001",
            "fecha": "2025-04-03T14:30:00Z",
            "duracion_segundos": 300,
            "frecuencia_muestreo": 256,
            "electrodos": ["Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2"],
            "sistema_colocacion": "10-20"
        },
        "eventos": [
            {
                "tipo": "pico",
                "canal": "Fp1",
                "tiempo": 2.134,
                "amplitud": 75.3,
                "frecuencia_dominante": "4.5Hz"
            },
            {
                "tipo": "artefacto",
                "canal": "Fp2",
                "tiempo": 10.250,
                "descripcion": "Movimiento ocular detectado",
                "nivel_ruido": "alto"
            },
            {
                "tipo": "epileptiforme",
                "canales": ["F3", "C3"],
                "tiempo_inicio": 25.400,
                "tiempo_fin": 25.800,
                "descripcion": "Descarga punta-onda",
                "frecuencia": "3Hz"
            }
        ]
    }

def prediccion_view(request):
    """
    Vista principal para mostrar la predicción
    """
    datos_eeg = obtener_datos_examen()
    anomalias = detectar_anomalias(datos_eeg)
    prediccion = generar_prediccion(anomalias, datos_eeg['paciente'])
    
    context = {
        'paciente': datos_eeg['paciente'],
        'examen': datos_eeg['examen'],
        'anomalias': anomalias,
        'prediccion': prediccion
    }
    
    return render(request, 'manejador_prediccion/prediccion.html', context)

def api_prediccion(request):
    """
    API endpoint para obtener predicción en formato JSON
    """
    if request.method == 'GET':
        datos_eeg = obtener_datos_examen()
        anomalias = detectar_anomalias(datos_eeg)
        prediccion = generar_prediccion(anomalias, datos_eeg['paciente'])
        
        response_data = {
            'paciente': datos_eeg['paciente'],
            'examen_id': datos_eeg['examen']['id'],
            'anomalias': anomalias,
            'prediccion': prediccion,
            'status': 'success'
        }
        
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
