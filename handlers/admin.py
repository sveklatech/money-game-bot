import os
from telegram import Update
from telegram.ext import ContextTypes
from database.database import get_all_users, get_stats

ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = set(int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit())


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def admin_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    users = get_all_users()

    text = f"👥 *Пользователи бота: {len(users)}*\n\n"

    for u in users[:20]:
        uid = u["user_id"]
        name = u["full_name"] or u["username"] or f"ID {uid}"
        stats = get_stats(uid)
        day = stats.get("current_day", 0)
        proc = stats.get("process_count", 0)
        text += f"• {name} — День {day}/30, Процессов: {proc}\n"

    if len(users) > 20:
        text += f"\n_... и ещё {len(users) - 20} пользователей_"

    await update.message.reply_text(text, parse_mode="Markdown")


async def admin_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Использование: /broadcast <текст>")
        return

    message = " ".join(context.args)
    users = get_all_users()
    sent = 0
    failed = 0

    for u in users:
        try:
            await context.bot.send_message(
                chat_id=u["user_id"],
                text=message,
                parse_mode="Markdown"
            )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(f"✅ Отправлено: {sent}\n❌ Ошибок: {failed}")
