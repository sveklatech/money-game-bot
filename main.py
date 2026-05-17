import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        raise RuntimeError
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)

from config import BOT_TOKEN
from database.database import init_db
from services.scheduler import setup_scheduler

from handlers.start import start_handler, help_handler
from handlers.daily import (
    show_day_handler, complete_day_callback, onboarding_start_plan_callback,
    receive_evening_answer, EVENING_ANSWER
)
from handlers.process_handler import (
    get_process_conversation_handler, mini_process_handler
)
from handlers.journal import (
    journal_menu_handler, recent_entries_handler,
    get_gratitude_conversation, get_vocabulary_conversation, get_weekly_review_conversation
)
from handlers.library import (
    library_menu_handler, process_map_handler, concepts_menu_handler,
    concept_detail_handler, scenarios_menu_handler, scenario_detail_handler,
    manifesto_menu_handler, manifesto_part_handler,
    manifesto_command_handler, concepts_command_handler, scenarios_command_handler
)
from handlers.stats import stats_handler
from handlers.settings import (
    settings_menu_handler, toggle_notifications_callback, get_settings_conversation
)
from handlers.admin import admin_stats_handler, admin_broadcast_handler
from keyboards.keyboards import main_menu_keyboard

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


async def back_main_callback(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✦ _Я ЕСТЬ Сила и Присутствие Бога._\n\nГлавное меню:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )


def main():
    init_db()
    logger.info("Database initialized.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(get_process_conversation_handler())
    app.add_handler(get_gratitude_conversation())
    app.add_handler(get_vocabulary_conversation())
    app.add_handler(get_weekly_review_conversation())
    app.add_handler(get_settings_conversation())

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("day", show_day_handler))
    app.add_handler(CommandHandler("mini", mini_process_handler))
    app.add_handler(CommandHandler("journal", journal_menu_handler))
    app.add_handler(CommandHandler("gratitude", lambda u, c: None))
    app.add_handler(CommandHandler("stats", stats_handler))
    app.add_handler(CommandHandler("settings", settings_menu_handler))
    app.add_handler(CommandHandler("manifesto", manifesto_command_handler))
    app.add_handler(CommandHandler("concepts", concepts_command_handler))
    app.add_handler(CommandHandler("scenarios", scenarios_command_handler))
    app.add_handler(CommandHandler("admin", admin_stats_handler))
    app.add_handler(CommandHandler("broadcast", admin_broadcast_handler))

    app.add_handler(CallbackQueryHandler(back_main_callback, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(onboarding_start_plan_callback, pattern="^onboarding_start_plan$"))
    app.add_handler(CallbackQueryHandler(show_day_handler, pattern="^show_day$"))
    app.add_handler(CallbackQueryHandler(complete_day_callback, pattern="^complete_day_\\d+$"))
    app.add_handler(CallbackQueryHandler(mini_process_handler, pattern="^mini_process$"))
    app.add_handler(CallbackQueryHandler(journal_menu_handler, pattern="^journal_menu$"))
    app.add_handler(CallbackQueryHandler(journal_menu_handler, pattern="^journal_process$"))
    app.add_handler(CallbackQueryHandler(recent_entries_handler, pattern="^journal_recent$"))
    app.add_handler(CallbackQueryHandler(library_menu_handler, pattern="^library_menu$"))
    app.add_handler(CallbackQueryHandler(process_map_handler, pattern="^lib_process_map$"))
    app.add_handler(CallbackQueryHandler(concepts_menu_handler, pattern="^lib_concepts$"))
    app.add_handler(CallbackQueryHandler(concept_detail_handler, pattern="^concept_"))
    app.add_handler(CallbackQueryHandler(scenarios_menu_handler, pattern="^lib_scenarios$"))
    app.add_handler(CallbackQueryHandler(scenario_detail_handler, pattern="^scenario_\\d+$"))
    app.add_handler(CallbackQueryHandler(manifesto_menu_handler, pattern="^lib_manifesto$"))
    app.add_handler(CallbackQueryHandler(manifesto_part_handler, pattern="^manifesto_part"))
    app.add_handler(CallbackQueryHandler(stats_handler, pattern="^show_stats$"))
    app.add_handler(CallbackQueryHandler(settings_menu_handler, pattern="^settings_menu$"))
    app.add_handler(CallbackQueryHandler(toggle_notifications_callback, pattern="^toggle_notifications$"))

    setup_scheduler(app)

    logger.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
