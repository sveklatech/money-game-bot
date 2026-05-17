from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, CommandHandler
from database.database import get_user, start_plan, is_day_completed, complete_day, get_stats
from services.content import get_day
from keyboards.keyboards import (
    main_menu_keyboard, day_keyboard, onboarding_keyboard, week_summary_keyboard
)

WEEK_NAMES = {
    1: "Неделя 1 — Наблюдение",
    2: "Неделя 2 — Признательность",
    3: "Неделя 3 — Процесс",
    4: "Неделя 4 — Интеграция в бизнес",
    5: "Закрепление",
}

EVENING_ANSWER = 100


def format_day_message(day_data: dict, is_completed: bool, current_day: int) -> str:
    week_name = WEEK_NAMES.get(day_data["week"], "")
    completed_mark = "✅" if is_completed else "📅"

    text = (
        f"{completed_mark} *День {day_data['day']} / 30* — {week_name}\n"
        f"Фокус: _{day_data['focus']}_\n\n"
        f"*{day_data['title']}*\n\n"
        f"{day_data['task']}\n\n"
        f"✦ _{day_data['affirmation']}_"
    )

    if is_completed:
        text += "\n\n_✅ Этот день уже отмечен выполненным._"
    elif day_data["day"] < current_day:
        text += "\n\n_⬅ Предыдущий день_"

    return text


async def show_day_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = get_user(user_id)

    if not db_user or not db_user["plan_started_at"]:
        if update.message:
            await update.message.reply_text(
                "Ты ещё не начала 30-дневный план.",
                reply_markup=onboarding_keyboard()
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                "Ты ещё не начала 30-дневный план.",
                reply_markup=onboarding_keyboard()
            )
        return

    current_day = db_user["current_day"]
    if current_day == 0:
        current_day = 1

    if current_day > 30:
        msg = (
            "🎉 *Ты прошла все 30 дней!*\n\n"
            "Из проекта — в образ жизни.\n\n"
            "Утренний и вечерний ритуал — ежедневно.\n"
            "Процесс — при каждом дискомфорте.\n"
            "Воркбук — раз в неделю.\n"
            "Манифест — раз в месяц.\n\n"
            "✦ _Я ЕСТЬ Сила и Присутствие Бога._"
        )
        kb = main_menu_keyboard()
        if update.message:
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)
        elif update.callback_query:
            await update.callback_query.edit_message_text(msg, parse_mode="Markdown", reply_markup=kb)
        return

    day_data = get_day(current_day)
    if not day_data:
        return

    completed = is_day_completed(user_id, current_day)
    text = format_day_message(day_data, completed, current_day)
    kb = day_keyboard(current_day, completed)

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)


async def complete_day_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    day_number = int(query.data.split("_")[-1])
    day_data = get_day(day_number)

    if not day_data:
        return

    context.user_data["completing_day"] = day_number
    await query.edit_message_text(
        f"✦ *День {day_number} — {day_data['title']}*\n\n"
        f"_{day_data['evening_question']}_\n\n"
        f"Напиши свой ответ (или отправь /skip чтобы пропустить):",
        parse_mode="Markdown"
    )

    return EVENING_ANSWER


async def receive_evening_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    day_number = context.user_data.get("completing_day")

    if not day_number:
        return ConversationHandler.END

    answer = update.message.text if update.message.text != "/skip" else ""
    complete_day(user_id, day_number, answer)

    day_data = get_day(day_number)
    db_user = get_user(user_id)
    next_day = db_user["current_day"] if db_user else day_number + 1

    response = (
        f"✅ *День {day_number} завершён!*\n\n"
        f"✦ _{day_data['affirmation']}_\n\n"
    )

    if next_day <= 30:
        next_data = get_day(next_day)
        if next_data:
            response += f"Завтра — *День {next_day}: {next_data['title']}*"
    else:
        response += "🎉 Ты прошла все 30 дней! Из проекта — в образ жизни."

    await update.message.reply_text(response, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    context.user_data.pop("completing_day", None)
    return ConversationHandler.END


async def onboarding_start_plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    db_user = get_user(user_id)

    if not db_user:
        from database.database import create_user
        user = update.effective_user
        create_user(user.id, user.username or "", user.full_name or "")

    start_plan(user_id)

    day_data = get_day(1)
    text = (
        "🚀 *30-дневный план запущен!*\n\n"
        "Каждый день — задание и аффирмация.\n"
        "Не рывок. Не штурм. Постепенное расширение.\n\n"
        "─────────────────────\n\n"
        + format_day_message(day_data, False, 1)
    )

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=day_keyboard(1, False))
