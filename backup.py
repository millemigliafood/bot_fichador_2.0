import shutil
import os
from datetime import datetime

# Ruta del archivo de fichajes original
ruta_fichajes = 'datos/fichajes/fichajes.json'

# Carpeta donde guardará las copias de seguridad
directorio_backup = 'datos/backups/'

# Crear la carpeta de backups si no existe
os.makedirs(directorio_backup, exist_ok=True)

# Generar nombre de archivo con fecha y hora
fecha_backup = datetime.now().strftime("%Y%m%d%H%M%S")  # Esto da la fecha y hora en formato YYYYMMDDHHMMSS
nombre_backup = f'fichajes_backup_{fecha_backup}.json'
ruta_backup = os.path.join(directorio_backup, nombre_backup)

# Copiar el archivo de fichajes al directorio de backups
shutil.copy2(ruta_fichajes, ruta_backup)

print(f'Backup creado correctamente en: {ruta_backup}')