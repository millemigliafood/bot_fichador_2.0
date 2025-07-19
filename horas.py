# horas.py

import matplotlib.pyplot as plt  # Esto requiere que matplotlib esté instalado

# Función para generar el reporte de horas
def generar_reporte_horas(empleado, mes, anio):
    # Aquí va la lógica para generar el reporte de horas, incluyendo gráficos si lo deseas
    horas_trabajadas = 160  # Ejemplo, esto debería calcularse en base a los registros reales
    horas_extra = 20  # Ejemplo de horas extras
    horas_contrato = 140  # Ejemplo de horas dentro de contrato

    # Generamos el reporte en formato texto
    reporte = f"Reporte de horas de {empleado} para {mes}/{anio}:\n"
    reporte += f"Total horas trabajadas: {horas_trabajadas} horas\n"
    reporte += f"Total horas extras: {horas_extra} horas\n"
    reporte += f"Total horas dentro de contrato: {horas_contrato} horas\n"

    # Ahora generamos un gráfico (opcional)
    fig, ax = plt.subplots()
    ax.bar(["Horas dentro de contrato", "Horas extras"], [horas_contrato, horas_extra])
    ax.set_ylabel("Horas")
    ax.set_title(f"Horas trabajadas por {empleado} en {mes}/{anio}")
    plt.tight_layout()

    # Guardar el gráfico como una imagen
    plt.savefig(f"reporte_horas_{empleado}_{mes}_{anio}.png")
    plt.close()

    return reporte