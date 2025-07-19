import json
from datetime import datetime
import re

# Función para validar formato de fecha
def validar_fecha(fecha):
    # Validar el formato MM/AAAA o 'mes 2025'
    if re.match(r'^(0[1-9]|1[0-2])\/\d{4}$', fecha):  # MM/AAAA
        try:
            datetime.strptime(fecha, "%m/%Y")
            return True
        except ValueError:
            return False
    elif re.match(r'^[a-zA-Z]+ \d{4}$', fecha):  # 'mes 2025'
        try:
            datetime.strptime(fecha, "%B %Y")
            return True
        except ValueError:
            return False
    return False

# Función para guardar los datos de fichaje
def guardar_fichajes(datos):
    with open('fichajes.json', 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# Función para leer los fichajes
def leer_fichajes():
    try:
        with open('fichajes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Registro de fichaje manual (Entrada o salida)
def registrar_fichaje(user_id, nombre, tipo, fecha):
    datos = leer_fichajes()
    if not validar_fecha(fecha):
        print("Formato no válido. Usa MM/AAAA o 'junio 2025'.")
        return False

    ahora = datetime.now()
    fecha_formateada = datetime.strptime(fecha, "%m/%Y") if '/' in fecha else datetime.strptime(fecha, "%B %Y")
    
    if tipo == "entrada":
        datos.append({
            "id": user_id,
            "nombre": nombre,
            "fecha": fecha_formateada.strftime("%Y-%m-%d"),
            "hora_entrada": ahora.strftime("%H:%M:%S"),
            "hora_salida": None,
        })
    elif tipo == "salida":
        for f in reversed(datos):
            if f["id"] == user_id and f["hora_salida"] is None:
                f["hora_salida"] = ahora.strftime("%H:%M:%S")
                break
    guardar_fichajes(datos)
    return True