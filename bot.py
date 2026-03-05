import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import pytz
from config import BOT_TOKEN, TIMEZONE
from medications import (
    MEDICATIONS,
    get_summary_text,
    get_today_schedule,
    is_active,
    days_remaining,
)
import storage

TZ = pytz.timezone(TIMEZONE)
logger = logging.getLogger(__name__)


# ─── Helpers ────────────────────────────────────────────────────────────────

def get_med_by_id(med_id: str) -> dict | None:
    return next((m for m in MEDICATIONS if m["id"] == med_id), None)


# ─── Commands ────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 <b>Xin chào! Tôi là bot nhắc uống thuốc của bạn.</b>\n\n"
        "Tôi sẽ tự động nhắc bạn uống thuốc đúng giờ.\n\n"
        "📌 <b>Các lệnh:</b>\n"
        "  /today – Lịch thuốc hôm nay\n"
        "  /summary – Tổng hợp toàn bộ lịch\n"
        "  /status – Trạng thái hôm nay (đã uống gì)\n"
        "  /help – Hướng dẫn\n\n"
        "💊 Chúc bạn mau khỏe! 🌟"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_today_schedule()
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_summary_text()
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today_data = storage.get_today_status()
    today = datetime.now(TZ).date()
    lines = [f"📊 <b>Trạng thái hôm nay – {today.strftime('%d/%m/%Y')}</b>\n"]

    for med in MEDICATIONS:
        if not is_active(med):
            continue
        lines.append(f"{med['name']}")
        for s in med["schedules"]:
            taken = storage.is_taken(med["id"], s["time"])
            icon = "✅" if taken else "⏳"
            lines.append(f"  {icon} {s['emoji']} {s['time']} – {s['label']}")
        lines.append("")

    if len(lines) == 1:
        lines.append("🎉 Hôm nay không có thuốc nào!")

    total_doses = sum(
        len(m["schedules"]) for m in MEDICATIONS if is_active(m)
    )
    taken_count = len(today_data)
    lines.append(f"📈 Đã uống: <b>{taken_count}/{total_doses}</b> lần hôm nay")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ <b>Hướng dẫn sử dụng</b>\n\n"
        "/start – Khởi động bot\n"
        "/today – Xem lịch thuốc hôm nay\n"
        "/summary – Tổng hợp toàn bộ lịch uống thuốc\n"
        "/status – Xem bạn đã uống thuốc gì hôm nay\n"
        "/help – Hiện hướng dẫn này\n\n"
        "⏰ Bot sẽ tự nhắc bạn đúng giờ quy định.\n"
        "Nhấn <b>✅ Đã uống</b> sau khi nhận nhắc để ghi nhận."
    )
    await update.message.reply_text(text, parse_mode="HTML")


# ─── Callback: Inline button ────────────────────────────────────────────────

async def callback_taken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # "taken|med_id|time_slot"
    _, med_id, time_slot = data.split("|", 2)
    med = get_med_by_id(med_id)

    if not med:
        await query.edit_message_text("❌ Không tìm thấy thông tin thuốc.")
        return

    newly_marked = storage.mark_taken(med_id, time_slot)
    now = datetime.now(TZ).strftime("%H:%M")

    if newly_marked:
        text = (
            f"✅ <b>Đã ghi nhận!</b>\n\n"
            f"{med['name']}\n"
            f"⏰ {time_slot} – Xác nhận lúc {now}\n\n"
            f"💪 Tuyệt vời! Tiếp tục duy trì nhé!"
        )
    else:
        text = (
            f"ℹ️ Bạn đã xác nhận <b>{med['name']}</b> lúc {time_slot} rồi!\n"
            f"✅ Không cần nhấn lại."
        )

    await query.edit_message_text(text, parse_mode="HTML")


# ─── App builder ────────────────────────────────────────────────────────────

def build_app() -> Application:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("summary", cmd_summary))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(callback_taken, pattern=r"^taken\|"))
    return app
