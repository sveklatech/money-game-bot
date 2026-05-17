from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from database.database import save_process_entry, save_mini_process
from services.content import get_process_step, get_mini_process_text, get_process
from keyboards.keyboards import (
    process_step_keyboard, cancel_keyboard, discomfort_level_keyboard, main_menu_keyboard
)

SITUATION = 1
DISCOMFORT_LEVEL = 2
STEP_1 = 3
STEP_2 = 4
STEP_3 = 5
STEP_4 = 6
STEP_5 = 7
STEP_6 = 8
SAVE_ENTRY = 9


def format_step(step_data: dict) -> str:
    text = f"✦ *Шаг {step_data['number']} из 6 — {step_data['title']}*\n\n"
    text += f"_{step_data['instruction']}_\n\n"

    if "affirmation" in step_data:
        text += f"*{step_data['affirmation']}*\n\n"

    text += f"💬 {step_data['prompt']}"
    return text


async def start_process_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_process()
    intro = data["full_process"]["intro"]

    text = (
        f"⚡ *Процесс — 6 шагов*\n\n"
        f"_{intro}_\n\n"
        f"Прежде всего — *опиши ситуацию или ощущение*, с которым хочешь поработать.\n\n"
        f"Это может быть:\n"
        f"• страх, тревога, раздражение\n"
        f"• конкретная бизнес-ситуация\n"
        f"• цифра на счету\n"
        f"• разговор, который давит\n\n"
        f"Напиши всё как есть:"
    )

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())

    return SITUATION


async def receive_situation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["process_situation"] = update.message.text

    await update.message.reply_text(
        "Оцени интенсивность дискомфорта прямо сейчас:\n\n"
        "1 — почти ничего\n"
        "5 — заметно\n"
        "10 — очень сильно",
        reply_markup=discomfort_level_keyboard()
    )

    return DISCOMFORT_LEVEL


async def receive_discomfort_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    level = int(query.data.split("_")[1])
    context.user_data["process_discomfort"] = level

    step_data = get_process_step(1)
    text = format_step(step_data)

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=process_step_keyboard(1)
    )

    return STEP_1


async def process_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    step_num = int(query.data.split("_")[-1])

    if step_num > 6:
        return await _finish_process(update, context)

    step_data = get_process_step(step_num)
    if not step_data:
        return ConversationHandler.END

    text = format_step(step_data)
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=process_step_keyboard(step_num)
    )

    state_map = {1: STEP_1, 2: STEP_2, 3: STEP_3, 4: STEP_4, 5: STEP_5, 6: STEP_6}
    return state_map.get(step_num, STEP_6)


async def _finish_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    text = (
        "✦ *Процесс завершён*\n\n"
        "Ты только что вернула часть своей Силы.\n\n"
        "Как ты себя чувствуешь сейчас?\n"
        "Опиши состояние после Процесса — одним-двумя предложениями:"
    )

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())
    return SAVE_ENTRY


async def process_save_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "✦ *Процесс завершён*\n\n"
        "Как ты себя чувствуешь сейчас?\n"
        "Опиши состояние после Процесса:"
    )

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())
    return SAVE_ENTRY


async def process_skip_save_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    situation = context.user_data.get("process_situation", "")
    discomfort = context.user_data.get("process_discomfort", 0)

    save_process_entry(user_id, situation, discomfort, "", "")

    context.user_data.pop("process_situation", None)
    context.user_data.pop("process_discomfort", None)

    await query.edit_message_text(
        "✅ Процесс записан.\n\n✦ _Вау. Спасибо себе. Спасибо своему творению._",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

    return ConversationHandler.END


async def receive_state_after(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state_after = update.message.text
    situation = context.user_data.get("process_situation", "")
    discomfort = context.user_data.get("process_discomfort", 0)

    save_process_entry(user_id, situation, discomfort, state_after, "")

    context.user_data.pop("process_situation", None)
    context.user_data.pop("process_discomfort", None)

    await update.message.reply_text(
        "✅ *Записано в журнал Процесса.*\n\n"
        "✦ _Вау. Какое великолепное создание. Спасибо себе. Спасибо своему творению._\n\n"
        "Каждый Процесс — шаг расширения.",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

    return ConversationHandler.END


async def cancel_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("process_situation", None)
    context.user_data.pop("process_discomfort", None)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "Процесс отменён.",
            reply_markup=main_menu_keyboard()
        )
    elif update.message:
        await update.message.reply_text("Процесс отменён.", reply_markup=main_menu_keyboard())

    return ConversationHandler.END


async def mini_process_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_mini_process(user_id, "")

    text = get_mini_process_text()
    text += (
        "\n\n─────────────────────\n"
        "✅ *Мини-Процесс выполнен и записан.*\n\n"
        "✦ _Цифры — это дым. Сила — настоящая._"
    )

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())


def get_process_conversation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("process", start_process_handler),
            CallbackQueryHandler(start_process_handler, pattern="^start_process$"),
        ],
        states={
            SITUATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_situation)],
            DISCOMFORT_LEVEL: [CallbackQueryHandler(receive_discomfort_level, pattern="^discomfort_\\d+$")],
            STEP_1: [CallbackQueryHandler(process_step_callback, pattern="^process_step_")],
            STEP_2: [CallbackQueryHandler(process_step_callback, pattern="^process_step_")],
            STEP_3: [CallbackQueryHandler(process_step_callback, pattern="^process_step_")],
            STEP_4: [CallbackQueryHandler(process_step_callback, pattern="^process_step_")],
            STEP_5: [CallbackQueryHandler(process_step_callback, pattern="^process_step_")],
            STEP_6: [
                CallbackQueryHandler(process_save_callback, pattern="^process_save$"),
                CallbackQueryHandler(process_skip_save_callback, pattern="^process_skip_save$"),
                CallbackQueryHandler(_finish_process, pattern="^process_step_7$"),
            ],
            SAVE_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_state_after)],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_process, pattern="^cancel$"),
            CommandHandler("cancel", cancel_process),
        ],
        allow_reentry=True,
    )
