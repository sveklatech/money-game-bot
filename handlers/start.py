from telegram import Update
from telegram.ext import ContextTypes
from database.database import get_user, create_user
from keyboards.keyboards import main_menu_keyboard, onboarding_keyboard


WELCOME_TEXT = """✦ Добро пожаловать в практику Освобождения от Денежной Игры ✦

Этот бот — твой личный проводник по системе Роберта Шейнфелда.

Здесь ты:
• Проходишь 30-дневный план интеграции
• Запускаешь Процесс (6 шагов) в момент дискомфорта
• Ведёшь журнал воркбука
• Работаешь с Манифестом Фазы 2

Всё создано твоим Сознанием.
Всё, что ты чувствуешь — Сила, ожидающая возвращения.

Дискомфорт — это мигающий красный сигнал: «Здесь Сила! Забери меня!»"""


RETURNING_TEXT = """✦ С возвращением! ✦

Ты — Сила и Присутствие Бога.
Всё, что произошло с момента твоей последней практики — твоё творение."""


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_user(user.id)

    if not db_user:
        create_user(user.id, user.username or "", user.full_name or "")
        await update.message.reply_text(
            WELCOME_TEXT,
            parse_mode="Markdown",
            reply_markup=onboarding_keyboard()
        )
    else:
        await update.message.reply_text(
            RETURNING_TEXT,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """📋 *Команды бота*

/start — главное меню
/day — задание текущего дня
/process — запустить Процесс (6 шагов)
/mini — Мини-Процесс
/journal — журнал
/gratitude — записать Признательность
/stats — статистика практики
/settings — настройки уведомлений
/manifesto — Манифест Фазы 2
/concepts — карта концепций
/scenarios — бизнес-сценарии

Или используй кнопки в главном меню."""

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
