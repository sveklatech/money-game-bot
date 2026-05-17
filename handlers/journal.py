from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from database.database import (
    save_gratitude, save_vocabulary, save_weekly_review,
    get_recent_process_entries, get_recent_gratitude, get_user
)
from keyboards.keyboards import journal_menu_keyboard, main_menu_keyboard, cancel_keyboard, back_keyboard

WAITING_GRATITUDE = 200
WAITING_VOCAB_P1 = 201
WAITING_VOCAB_P2 = 202
WAITING_REVIEW_CHANGES = 203
WAITING_REVIEW_PATTERNS = 204
WAITING_REVIEW_INSIGHTS = 205


async def journal_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📔 *Журнал практики*\n\nЧто хочешь записать?"

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=journal_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=journal_menu_keyboard())


async def start_gratitude_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🙏 *Журнал Признательности*\n\n"
        "Напиши, за что ты сейчас Признаёшь:\n"
        "— себя как Творца\n"
        "— своё творение (ситуацию, человека, результат)\n"
        "— момент дня\n\n"
        "Одна запись — одно Признание. Или несколько через перенос строки:"
    )

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())

    return WAITING_GRATITUDE


async def receive_gratitude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_gratitude(user_id, update.message.text)

    await update.message.reply_text(
        "✅ *Записано.*\n\n✦ _Вау. Я создала это. Спасибо себе как Творцу._",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

    return ConversationHandler.END


async def start_vocabulary_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💬 *Словарь Фазы 1 → Фаза 2*\n\n"
        "Напиши фразу из Фазы 1, которую ты сегодня поймала:\n\n"
        "Например: «не могу позволить», «надо заработать», «дорого»"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())
    elif update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())

    return WAITING_VOCAB_P1


async def receive_vocab_p1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["vocab_p1"] = update.message.text

    await update.message.reply_text(
        f"Фраза Фазы 1: *\"{update.message.text}\"*\n\n"
        f"Теперь напиши её замену в Фазе 2:\n\n"
        f"Например: «я выбираю иначе распределить Признательность»",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

    return WAITING_VOCAB_P2


async def receive_vocab_p2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    p1 = context.user_data.pop("vocab_p1", "")
    p2 = update.message.text

    save_vocabulary(user_id, p1, p2)

    await update.message.reply_text(
        f"✅ *Записано в словарь:*\n\n"
        f"_{p1}_ → *{p2}*\n\n"
        f"✦ _Слова формируют поле._",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

    return ConversationHandler.END


async def recent_entries_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    entries = get_recent_process_entries(user_id, limit=3)
    gratitude = get_recent_gratitude(user_id, limit=3)

    text = "📖 *Последние записи*\n\n"

    if entries:
        text += "⚡ *Дневник Процесса:*\n"
        for e in entries:
            date = e["created_at"][:10]
            text += f"• {date} — _{e['situation'][:60]}..._\n" if len(e["situation"]) > 60 else f"• {date} — _{e['situation']}_\n"
        text += "\n"
    else:
        text += "⚡ Записей Процесса пока нет.\n\n"

    if gratitude:
        text += "🙏 *Журнал Признательности:*\n"
        for g in gratitude:
            date = g["created_at"][:10]
            text += f"• {date} — _{g['text'][:60]}..._\n" if len(g["text"]) > 60 else f"• {date} — _{g['text']}_\n"
    else:
        text += "🙏 Записей Признательности пока нет."

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=journal_menu_keyboard())


async def start_weekly_review_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    week_num = int(data.split("_")[-1])
    context.user_data["review_week"] = week_num

    await query.edit_message_text(
        f"📝 *Еженедельный обзор — Неделя {week_num}*\n\n"
        f"*Что изменилось в ощущении денег или бизнеса за эту неделю?*\n\n"
        f"Напиши несколько строк — что заметила, что почувствовала:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

    return WAITING_REVIEW_CHANGES


async def receive_review_changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["review_changes"] = update.message.text

    await update.message.reply_text(
        "*Какие паттерны открылись? Где была Сила?*\n\n"
        "Что повторялось, что удивило, что было самым заряженным:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

    return WAITING_REVIEW_PATTERNS


async def receive_review_patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["review_patterns"] = update.message.text

    await update.message.reply_text(
        "*Главный инсайт недели:*\n\n"
        "Одна фраза или мысль, которую хочешь запомнить:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

    return WAITING_REVIEW_INSIGHTS


async def receive_review_insights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    week = context.user_data.pop("review_week", 0)
    changes = context.user_data.pop("review_changes", "")
    patterns = context.user_data.pop("review_patterns", "")
    insights = update.message.text

    save_weekly_review(user_id, week, changes, patterns, insights)

    await update.message.reply_text(
        f"✅ *Обзор недели {week} сохранён.*\n\n"
        f"✦ _{insights}_\n\n"
        f"_Расширение идёт._",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

    return ConversationHandler.END


async def cancel_journal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for key in ["vocab_p1", "review_week", "review_changes", "review_patterns"]:
        context.user_data.pop(key, None)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Отменено.", reply_markup=main_menu_keyboard())
    elif update.message:
        await update.message.reply_text("Отменено.", reply_markup=main_menu_keyboard())

    return ConversationHandler.END


def get_gratitude_conversation():
    return ConversationHandler(
        entry_points=[
            CommandHandler("gratitude", start_gratitude_handler),
            CallbackQueryHandler(start_gratitude_handler, pattern="^journal_gratitude$"),
        ],
        states={
            WAITING_GRATITUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_gratitude)],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_journal, pattern="^cancel$"),
            CommandHandler("cancel", cancel_journal),
        ],
        allow_reentry=True,
    )


def get_vocabulary_conversation():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_vocabulary_handler, pattern="^journal_vocabulary$"),
        ],
        states={
            WAITING_VOCAB_P1: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_vocab_p1)],
            WAITING_VOCAB_P2: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_vocab_p2)],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_journal, pattern="^cancel$"),
            CommandHandler("cancel", cancel_journal),
        ],
        allow_reentry=True,
    )


def get_weekly_review_conversation():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_weekly_review_handler, pattern="^write_weekly_review_\\d+$"),
        ],
        states={
            WAITING_REVIEW_CHANGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_review_changes)],
            WAITING_REVIEW_PATTERNS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_review_patterns)],
            WAITING_REVIEW_INSIGHTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_review_insights)],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_journal, pattern="^cancel$"),
            CommandHandler("cancel", cancel_journal),
        ],
        allow_reentry=True,
    )
