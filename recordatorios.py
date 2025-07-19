from geopy.distance import geodesic

# Función para comprobar si un empleado está cerca del lugar de trabajo
def verificar_geolocalizacion(ubicacion_empleado, ubicacion_trabajo):
    distancia = geodesic(ubicacion_empleado, ubicacion_trabajo).km
    if distancia < 1:
        return True  # Está cerca del trabajo
    return False

# Función para enviar recordatorio
def enviar_recordatorio(empleado, tipo_fichaje):
    if tipo_fichaje == "entrada":
        print(f"¡Hola {empleado}! Recuerda fichar tu entrada.")
    elif tipo_fichaje == "salida":
        print(f"¡Hola {empleado}! Recuerda fichar tu salida.")