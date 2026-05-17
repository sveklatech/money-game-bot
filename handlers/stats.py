from telegram import Update
from telegram.ext import ContextTypes
from database.database import get_stats, get_user
from keyboards.keyboards import main_menu_keyboard


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_stats(user_id)

    if not stats:
        text = "У тебя ещё нет данных. Начни практику!"
        if update.message:
            await update.message.reply_text(text, reply_markup=main_menu_keyboard())
        elif update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard())
        return

    current_day = stats.get("current_day", 0)
    plan_text = f"День {current_day} / 30" if current_day and current_day <= 30 else ("Не начат" if not current_day else "✅ Все 30 дней пройдены")

    started = stats.get("plan_started_at", "")
    started_text = started[:10] if started else "—"

    text = (
        "📊 *Статистика практики*\n\n"
        f"📅 *30-дневный план:* {plan_text}\n"
        f"🗓 Начат: {started_text}\n"
        f"✅ Дней завершено: {stats['days_completed']}\n\n"
        f"⚡ *Процессов проведено:* {stats['process_count']}\n"
        f"✨ *Мини-процессов:* {stats['mini_count']}\n"
        f"🙏 *Записей Признательности:* {stats['gratitude_count']}\n\n"
        f"_Каждый Процесс — шаг возвращения Силы._\n"
        f"_Каждая запись — след расширения._"
    )

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
