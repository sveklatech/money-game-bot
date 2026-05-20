import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram.ext import Application
from database.database import get_all_users, get_stats
from services.content import get_day, get_morning_ritual, get_evening_ritual

logger = logging.getLogger(__name__)

_DEFAULT_TZ = ZoneInfo("Europe/Moscow")


def _user_now(user) -> datetime:
    tz_name = user["timezone"] if user["timezone"] else "Europe/Moscow"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = _DEFAULT_TZ
    return datetime.now(tz)


async def send_morning_notification(context):
    users = get_all_users()
    ritual = get_morning_ritual()

    for user in users:
        try:
            morning_time = user["morning_time"] or "08:00"
            h, m = map(int, morning_time.split(":"))

            now = _user_now(user)
            if now.hour != h or abs(now.minute - m) > 1:
                continue

            user_id = user["user_id"]
            stats = get_stats(user_id)
            current_day = stats.get("current_day", 0)

            day_text = ""
            if current_day and 1 <= current_day <= 30:
                day_data = get_day(current_day)
                if day_data:
                    task = day_data["task"]
                    day_text = (
                        f"\n\n📅 *Сегодня — День {current_day}: {day_data['title']}*\n"
                        f"_{task[:200]}..._" if len(task) > 200
                        else f"\n\n📅 *Сегодня — День {current_day}: {day_data['title']}*\n_{task}_"
                    )

            text = (
                f"☀️ *Доброе утро!*\n\n"
                f"🌅 *Утренний ритуал:*\n_{ritual}_"
                + day_text +
                f"\n\n✦ _Я создаю всё, что испытаю сегодня._"
            )

            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Morning notification error for {user.get('user_id')}: {e}")


async def send_evening_notification(context):
    users = get_all_users()
    ritual = get_evening_ritual()

    for user in users:
        try:
            evening_time = user["evening_time"] or "21:00"
            h, m = map(int, evening_time.split(":"))

            now = _user_now(user)
            if now.hour != h or abs(now.minute - m) > 1:
                continue

            user_id = user["user_id"]
            stats = get_stats(user_id)
            current_day = stats.get("current_day", 0)

            text = (
                f"🌙 *Добрый вечер!*\n\n"
                f"Время вечернего ритуала.\n\n"
                f"💭 Прокрути день: где был дискомфорт? Где была Признательность?\n\n"
                f"🌙 *Вечерний ритуал:*\n_{ritual}_\n\n"
            )

            if current_day and 1 <= current_day <= 30:
                day_data = get_day(current_day)
                if day_data:
                    text += (
                        f"❓ *Вопрос дня {current_day}:*\n"
                        f"_{day_data['evening_question']}_\n\n"
                        f"Напиши ответ или открой /day чтобы отметить день выполненным."
                    )

            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Evening notification error for {user.get('user_id')}: {e}")


def setup_scheduler(app: Application):
    job_queue = app.job_queue

    job_queue.run_repeating(
        send_morning_notification,
        interval=60,
        first=10,
        name="morning_notifications"
    )

    job_queue.run_repeating(
        send_evening_notification,
        interval=60,
        first=30,
        name="evening_notifications"
    )

    logger.info("Scheduler set up: morning and evening notifications active.")
