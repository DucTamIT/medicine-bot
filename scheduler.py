import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from config import CHAT_ID, TIMEZONE
from medications import MEDICATIONS, is_active, days_remaining
import storage

TZ = pytz.timezone(TIMEZONE)
logger = logging.getLogger(__name__)

_bot_app = None


def set_bot(app):
    global _bot_app
    _bot_app = app


def _make_reminder_job(med: dict, time_slot: str, label: str, emoji: str):
    async def send_reminder():
        if not _bot_app:
            return
        if not is_active(med):
            logger.info(f"Thuốc {med['name']} đã hết hạn, bỏ qua nhắc nhở.")
            return

        already = storage.is_taken(med["id"], time_slot)
        if already:
            return  # Đã uống rồi, không nhắc nữa

        remaining = days_remaining(med)

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "✅ Đã uống / Đã dùng",
                callback_data=f"taken|{med['id']}|{time_slot}"
            )
        ]])

        text = (
            f"⏰ <b>Nhắc nhở {label}</b>\n\n"
            f"{emoji} <b>{med['name']}</b>\n"
            f"📝 {med['note']}\n"
            f"📅 Còn <b>{remaining} ngày</b> nữa\n\n"
            f"Nhấn nút bên dưới để xác nhận đã uống! 👇"
        )

        await _bot_app.bot.send_message(
            chat_id=CHAT_ID,
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        logger.info(f"Đã gửi nhắc nhở: {med['name']} - {time_slot}")

    return send_reminder


def setup_scheduler():
    scheduler = AsyncIOScheduler(timezone=TZ)

    for med in MEDICATIONS:
        for s in med["schedules"]:
            hour, minute = map(int, s["time"].split(":"))
            job_func = _make_reminder_job(med, s["time"], s["label"], s["emoji"])
            scheduler.add_job(
                job_func,
                trigger=CronTrigger(hour=hour, minute=minute, timezone=TZ),
                id=f"{med['id']}_{s['time'].replace(':', '')}",
                name=f"{med['name']} - {s['label']}",
                replace_existing=True,
            )
            logger.info(f"Đã lên lịch: {med['name']} lúc {s['time']}")

    # Gửi tổng hợp mỗi sáng 6:45
    async def send_morning_summary():
        if not _bot_app:
            return
        from medications import get_today_schedule
        text = "🌞 <b>Chào buổi sáng!</b> Đây là lịch thuốc hôm nay:\n\n" + get_today_schedule()
        await _bot_app.bot.send_message(
            chat_id=CHAT_ID, text=text, parse_mode="HTML"
        )

    scheduler.add_job(
        send_morning_summary,
        trigger=CronTrigger(hour=6, minute=45, timezone=TZ),
        id="morning_summary",
        name="Tổng hợp buổi sáng",
        replace_existing=True,
    )

    return scheduler
