import json
import time

# Función para planificar turnos
def planificar_turnos():
    empleados = [
        {"id": "8002770837", "nombre": "🫀", "horas_contrato": 40},
        {"id": "5607347615", "nombre": "Eduardo", "horas_contrato": 40},
        {"id": "6487791851", "nombre": "Yub", "horas_contrato": 40},
        {"id": "8062445172", "nombre": "Ana", "horas_contrato": 30},
        {"id": "6656164768", "nombre": "Diana", "horas_contrato": 40},
    ]
    turnos_disponibles = {
        "lunes": ["12:00-16:00", "20:00-00:00"],
        "martes": ["12:00-16:00", "20:00-00:00"],
        "miércoles": ["12:00-16:00", "20:00-00:00"],
        "jueves": ["12:00-16:00", "20:00-00:00"],
        "viernes": ["12:00-16:00", "20:00-00:00"],
        "sábado": ["12:00-16:00", "20:00-00:00"],
        "domingo": ["12:00-16:00", "20:00-00:00"],
    }

    # Selección de empleados
    empleados_seleccionados = input("Selecciona los empleados separados por coma: ").split(",")
    turnos_asignados = {}
    
    # Asignación de turnos
    for empleado_id in empleados_seleccionados:
        empleado = next(e for e in empleados if e["id"] == empleado_id.strip())
        horas_disponibles = empleado["horas_contrato"]
        
        # Asignar días
        for dia, turnos in turnos_disponibles.items():
            print(f"Turnos disponibles para {dia}: {', '.join(turnos)}")
            turno_seleccionado = input(f"Selecciona el turno para {empleado['nombre']} el {dia}: ")
            horas_asignadas = 4 if turno_seleccionado in turnos else 0
            horas_disponibles -= horas_asignadas
            if horas_disponibles < 0:
                print(f"No puedes asignar más horas a {empleado['nombre']}")
            else:
                turnos_asignados[empleado['nombre']] = turno_seleccionado
                print(f"{empleado['nombre']} asignado al turno {turno_seleccionado}")
                
    return turnos_asignados
