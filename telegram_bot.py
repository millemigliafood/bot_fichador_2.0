import logging
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from fichajes import registrar_fichaje, validar_fecha, leer_fichajes
from turnos import planificar_turnos
from horas import generar_reporte_horas
from recordatorios import enviar_recordatorio, verificar_geolocalizacion

TOKEN = '8174097868:AAFzP4wkQFh9gxJhir0rIo5I-Q9JEfsADZ4'

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ——— Construye el menú inline principal ———
def menu_principal() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗓 Horas por mes",    callback_data='horas_por_mes'),
         InlineKeyboardButton("📊 Resumen",          callback_data='resumen')],
        [InlineKeyboardButton("🔍 Ver detallados",  callback_data='ver_detallados')],
        [InlineKeyboardButton("✅ Fichar entrada",   callback_data='fichar_entrada'),
         InlineKeyboardButton("🏁 Fichar salida",    callback_data='fichar_salida')],
        [InlineKeyboardButton("📋 Planificar turnos",callback_data='planificar_turnos'),
         InlineKeyboardButton("✍️ Fichaje manual",   callback_data='fichaje_manual')],
    ])

# ——— /start ———
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saluda y muestra el menú."""
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"¡Hola {user}! Elige una acción:",
        reply_markup=menu_principal()
    )
    context.user_data.clear()

# ——— Router de botones ———
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    acción = q.data
    user = q.from_user.first_name
    await q.answer()

    # 1) Horas por mes → envía imagen
    if acción == 'horas_por_mes':
        mes, año = datetime.now().month, datetime.now().year
        ruta_png = generar_reporte_horas(user, mes, año)
        await q.message.reply_photo(open(ruta_png, 'rb'))
        return await q.message.reply_text("Menú:", reply_markup=menu_principal())

    # 2) Resumen → pide rango de fechas
    if acción == 'resumen':
        context.user_data['modo'] = 'resumen'
        return await q.message.reply_text(
            "Escribe rango DD/MM/AAAA-DD/MM/AAAA:",
            reply_markup=menu_principal()
        )

    # 3) Ver detallados → lista de hoy
    if acción == 'ver_detallados':
        hoy = datetime.now().strftime("%d/%m/%Y")
        todos = leer_fichajes()
        lista = [f"{f['hora']} {f['usuario']} {f['tipo']}" 
                 for f in todos if f['fecha'].startswith(hoy)]
        texto = "\n".join(lista) or "No hay fichajes hoy."
        await q.message.reply_text(texto)
        return await q.message.reply_text("Menú:", reply_markup=menu_principal())

    # 4) Fichar entrada → pide ubicación
    if acción == 'fichar_entrada':
        context.user_data['modo'] = 'geo_entrada'
        return await q.message.reply_text(
            "🔔 Comparte tu ubicación para fichar ENTRADA",
            reply_markup=menu_principal()
        )

    # 5) Fichar salida → pide ubicación
    if acción == 'fichar_salida':
        context.user_data['modo'] = 'geo_salida'
        return await q.message.reply_text(
            "🔔 Comparte tu ubicación para fichar SALIDA",
            reply_markup=menu_principal()
        )

    # 6) Planificar turnos → supón que aquí ya has seleccionado empleados
    if acción == 'planificar_turnos':
        # Ejemplo estático; en tu versión tendrás un submenú de empleados:
        empleados = context.user_data.get('seleccionados', [])
        texto = planificar_turnos(empleados)
        await q.message.reply_text(f"Turnos:\n{texto}")
        return await q.message.reply_text("Menú:", reply_markup=menu_principal())

    # 7) Fichaje manual → pide parámetros
    if acción == 'fichaje_manual':
        context.user_data['modo'] = 'manual'
        return await q.message.reply_text(
            "✏️ Envía: ID_USUARIO ENTRADA|SALIDA DD/MM/AAAA HH:MM:SS",
            reply_markup=menu_principal()
        )

    # 8) Por defecto, vuelve a mostrar menú
    return await q.message.reply_text("Menú:", reply_markup=menu_principal())

# ——— Mensajes de texto (resumen y manual) ———
async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    modo = context.user_data.get('modo')
    user = update.effective_user.first_name
    txt = update.message.text.strip()

    # Resumen de fechas
    if modo == 'resumen':
        try:
            ini, fin = txt.split('-')
            di = datetime.strptime(ini.strip(), "%d/%m/%Y")
            df = datetime.strptime(fin.strip(), "%d/%m/%Y")
        except:
            return await update.message.reply_text(
                "Formato inválido.", reply_markup=menu_principal()
            )
        hits = [f for f in leer_fichajes()
                if f['usuario']==user and 
                   di <= datetime.strptime(f['fecha'], "%d/%m/%Y %H:%M:%S") <= df]
        e = sum(1 for f in hits if f['tipo']=='entrada')
        s = sum(1 for f in hits if f['tipo']=='salida')
        await update.message.reply_text(
            f"Entradas: {e}, Salidas: {s}", reply_markup=menu_principal()
        )
        context.user_data.clear()
        return

    # Fichaje manual
    if modo == 'manual':
        partes = txt.split()
        if len(partes)!=4:
            return await update.message.reply_text(
                "Formato inválido.", reply_markup=menu_principal()
            )
        uid, tipo, fecha, hora = partes
        ts = f"{fecha} {hora}"
        registrar_fichaje(int(uid), tipo.lower(), ts, user)
        await update.message.reply_text("✅ Fichaje manual guardado.", reply_markup=menu_principal())
        context.user_data.clear()
        return

    # Si no estaba en modo, invito a usar el menú
    await update.message.reply_text("Pulsa un botón del menú.", reply_markup=menu_principal())

# ——— Mensajes de ubicación ———
async def on_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    modo = context.user_data.get('modo')
    if modo not in ('geo_entrada','geo_salida'):
        return
    lat, lon = update.message.location.latitude, update.message.location.longitude
    tipo = 'entrada' if modo=='geo_entrada' else 'salida'
    if verificar_geolocalizacion((lat, lon), (40.4168, -3.7038)):
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        registrar_fichaje(update.effective_chat.id, tipo, ts, update.effective_user.first_name)
        await update.message.reply_text(f"✅ {tipo.capitalize()} a las {ts}", reply_markup=menu_principal())
    else:
        await update.message.reply_text("🚫 Fuera de rango.", reply_markup=menu_principal())
    context.user_data.clear()

# ——— Montaje final ———
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(filters.LOCATION, on_location))
    app.run_polling()

if __name__ == "__main__":
    main()
