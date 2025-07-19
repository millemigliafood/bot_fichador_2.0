import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from datetime import datetime
from fichajes import registrar_fichaje, validar_fecha, leer_fichajes
from turnos import planificar_turnos
from horas import generar_reporte_horas
from recordatorios import enviar_recordatorio, verificar_geolocalizacion

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Ver fichajes", callback_data='ver_fichajes')],
        [InlineKeyboardButton("Registrar fichaje", callback_data='registrar_fichaje')],
        [InlineKeyboardButton("Planificar turnos", callback_data='planificar_turnos')],
        [InlineKeyboardButton("Generar reporte de horas", callback_data='reporte_horas')],
        [InlineKeyboardButton("Recordatorio de fichaje", callback_data='recordatorio')]
    ]
    await update.effective_message.reply_text(
        f"¡Hola {user.first_name}! ¿Qué deseas hacer?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def ver_fichajes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    keyboard = [
        [InlineKeyboardButton("Ver mes específico", callback_data='mes_especifico')],
        [InlineKeyboardButton("Volver al menú principal", callback_data='start')]
    ]
    await update.callback_query.edit_message_text(
        "Selecciona un mes (MM/AAAA o 'junio 2025'):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def registrar_fichaje_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    keyboard = [
        [InlineKeyboardButton("Entrada", callback_data='entrada')],
        [InlineKeyboardButton("Salida", callback_data='salida')],
        [InlineKeyboardButton("Volver al menú principal", callback_data='start')]
    ]
    await update.callback_query.edit_message_text(
        "Selecciona el tipo de fichaje:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def planificar_turnos_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    keyboard = [
        [InlineKeyboardButton("Planificar turnos", callback_data='confirmar_planificacion')],
        [InlineKeyboardButton("Volver al menú principal", callback_data='start')]
    ]
    await update.callback_query.edit_message_text(
        "Selecciona los turnos a asignar:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def generar_reporte(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    keyboard = [
        [InlineKeyboardButton("Generar reporte", callback_data='generar_reporte')],
        [InlineKeyboardButton("Volver al menú principal", callback_data='start')]
    ]
    await update.callback_query.edit_message_text(
        "Generando reporte de horas trabajadas...",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def recordatorio_fichaje(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    empleado = update.effective_user.first_name
    lat, lon = update.effective_message.location.latitude, update.effective_message.location.longitude
    if verificar_geolocalizacion((lat, lon), (40.4168, -3.7038)):
        enviar_recordatorio(empleado, "fichaje")
        await update.effective_message.reply_text("¡Recordatorio enviado!")
    else:
        await update.effective_message.reply_text("Parece que no estás cerca del lugar de trabajo.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == 'ver_fichajes':
        await ver_fichajes(update, context)

    elif data == 'registrar_fichaje':
        await registrar_fichaje_cmd(update, context)

    # Aquí manejamos los dos nuevos casos:
    elif data in ('entrada', 'salida'):
        tipo = data  # "entrada" o "salida"
        chat_id = query.message.chat_id
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # Llamada a tu función real; ajústala si tu firma es distinta:
        registrar_fichaje(chat_id, tipo, now)
        await query.edit_message_text(f"✅ {tipo.capitalize()} registrada manualmente a las {now}")
        # Volvemos al menú principal si quieres:
        await start(update, context)

    elif data == 'planificar_turnos':
        await planificar_turnos_cmd(update, context)

    elif data == 'reporte_horas':
        await generar_reporte(update, context)

    elif data == 'recordatorio':
        await query.edit_message_text("Por favor, envía tu ubicación para verificar tu cercanía.")

    elif data == 'start':
        await start(update, context)

    else:
        await query.edit_message_text("Opción no reconocida. Regresando al menú principal...")
        await start(update, context)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)

def main() -> None:
    TOKEN = '8174097868:AAFzP4wkQFh9gxJhir0rIo5I-Q9JEfsADZ4'
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.LOCATION, recordatorio_fichaje))
    # Cualquier texto reabre el menú
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_start))

    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()