from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from database.database import get_user, update_settings
from keyboards.keyboards import settings_keyboard, main_menu_keyboard, cancel_keyboard

WAITING_MORNING_TIME = 300
WAITING_EVENING_TIME = 301

TIME_HELP = "Введи время в формате ЧЧ:ММ, например: 08:00 или 21:30"


async def settings_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    notif_on = bool(user["notifications_enabled"]) if user else True
    morning = user["morning_time"] if user else "08:00"
    evening = user["evening_time"] if user else "21:00"

    text = (
        f"⚙️ *Настройки*\n\n"
        f"⏰ Утреннее напоминание: *{morning}*\n"
        f"🌙 Вечернее напоминание: *{evening}*\n"
        f"🔔 Уведомления: *{'включены' if notif_on else 'выключены'}*"
    )

    kb = settings_keyboard(notif_on)

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)


async def toggle_notifications_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    current = bool(user["notifications_enabled"]) if user else True
    new_val = 0 if current else 1

    update_settings(user_id, notifications_enabled=new_val)

    state_text = "включены ✅" if new_val else "выключены 🔕"
    await query.answer(f"Уведомления {state_text}", show_alert=True)

    user = get_user(user_id)
    notif_on = bool(user["notifications_enabled"])
    morning = user["morning_time"]
    evening = user["evening_time"]

    text = (
        f"⚙️ *Настройки*\n\n"
        f"⏰ Утреннее напоминание: *{morning}*\n"
        f"🌙 Вечернее напоминание: *{evening}*\n"
        f"🔔 Уведомления: *{'включены' if notif_on else 'выключены'}*"
    )

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=settings_keyboard(notif_on))


async def set_morning_time_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        f"⏰ *Время утреннего напоминания*\n\n{TIME_HELP}",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

    return WAITING_MORNING_TIME


async def receive_morning_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = update.message.text.strip()

    if not _valid_time(time_str):
        await update.message.reply_text(
            f"Неверный формат. {TIME_HELP}",
            reply_markup=cancel_keyboard()
        )
        return WAITING_MORNING_TIME

    user_id = update.effective_user.id
    update_settings(user_id, morning_time=time_str)

    await update.message.reply_text(
        f"✅ Утреннее напоминание установлено на *{time_str}*",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

    return ConversationHandler.END


async def set_evening_time_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        f"🌙 *Время вечернего напоминания*\n\n{TIME_HELP}",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

    return WAITING_EVENING_TIME


async def receive_evening_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = update.message.text.strip()

    if not _valid_time(time_str):
        await update.message.reply_text(
            f"Неверный формат. {TIME_HELP}",
            reply_markup=cancel_keyboard()
        )
        return WAITING_EVENING_TIME

    user_id = update.effective_user.id
    update_settings(user_id, evening_time=time_str)

    await update.message.reply_text(
        f"✅ Вечернее напоминание установлено на *{time_str}*",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

    return ConversationHandler.END


async def cancel_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Отменено.", reply_markup=main_menu_keyboard())
    elif update.message:
        await update.message.reply_text("Отменено.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END


def _valid_time(t: str) -> bool:
    try:
        parts = t.split(":")
        if len(parts) != 2:
            return False
        h, m = int(parts[0]), int(parts[1])
        return 0 <= h <= 23 and 0 <= m <= 59
    except Exception:
        return False


def get_settings_conversation():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(set_morning_time_start, pattern="^set_morning_time$"),
            CallbackQueryHandler(set_evening_time_start, pattern="^set_evening_time$"),
        ],
        states={
            WAITING_MORNING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_morning_time)],
            WAITING_EVENING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_evening_time)],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_settings, pattern="^cancel$"),
            CommandHandler("cancel", cancel_settings),
        ],
        allow_reentry=True,
    )
