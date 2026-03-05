from datetime import date, datetime
import pytz
from config import TIMEZONE

TZ = pytz.timezone(TIMEZONE)

# Ngày bắt đầu: 6/3/2026
START_DATE = date(2026, 3, 6)

MEDICATIONS = [
    {
        "id": "xit_mui",
        "name": "💊 Thuốc xịt mũi",
        "duration_days": 14,
        "note": "Xịt mũi 1 lần",
        "schedules": [
            {"time": "06:00", "label": "Buổi sáng", "emoji": "🌅"},
        ],
    },
    {
        "id": "thuoc_hit",
        "name": "💨 Thuốc hít",
        "duration_days": 60,
        "note": "Hít 1 lần",
        "schedules": [
            {"time": "06:00", "label": "Buổi sáng", "emoji": "🌅"},
            {"time": "20:00", "label": "Buổi tối", "emoji": "🌙"},
        ],
    },
    {
        "id": "rua_mat",
        "name": "🧴 Rửa mặt",
        "duration_days": 30,
        "note": "Rửa mặt sạch",
        "schedules": [
            {"time": "06:00", "label": "Buổi sáng", "emoji": "🌅"},
            {"time": "22:00", "label": "Buổi tối", "emoji": "🌙"},
        ],
    },
    {
        "id": "thuoc_uong_vi",
        "name": "💊 Thuốc uống vỉ",
        "duration_days": 30,
        "note": "Uống 2 viên sau khi ăn",
        "schedules": [
            {"time": "19:00", "label": "Tối sau khi ăn", "emoji": "🍽️"},
        ],
    },
    {
        "id": "thuoc_boi",
        "name": "🧴 Thuốc bôi",
        "duration_days": 10,
        "note": "Bôi sau khi rửa mặt",
        "schedules": [
            {"time": "06:00", "label": "Sau rửa mặt sáng", "emoji": "🌅"},
            {"time": "22:00", "label": "Sau rửa mặt tối", "emoji": "🌙"},
        ],
    },
    {
        "id": "thuoc_le",
        "name": "💊 Thuốc lẻ",
        "duration_days": 7,
        "note": "Uống 1 viên (tổng 7 viên)",
        "schedules": [
            {"time": "19:00", "label": "Sau khi ăn tối", "emoji": "🍽️"},
        ],
    },
]


def get_end_date(med: dict) -> date:
    from datetime import timedelta
    return START_DATE + timedelta(days=med["duration_days"] - 1)


def is_active(med: dict) -> bool:
    today = datetime.now(TZ).date()
    return START_DATE <= today <= get_end_date(med)


def days_remaining(med: dict) -> int:
    today = datetime.now(TZ).date()
    end = get_end_date(med)
    return max(0, (end - today).days + 1)


def days_passed(med: dict) -> int:
    today = datetime.now(TZ).date()
    if today < START_DATE:
        return 0
    end = get_end_date(med)
    return min((today - START_DATE).days + 1, med["duration_days"])


def get_summary_text() -> str:
    today = datetime.now(TZ).date()
    lines = [f"📋 <b>Tổng hợp lịch uống thuốc</b>"]
    lines.append(f"📅 Ngày bắt đầu: <b>{START_DATE.strftime('%d/%m/%Y')}</b>")
    lines.append(f"📆 Hôm nay: <b>{today.strftime('%d/%m/%Y')}</b>")
    lines.append("")

    for med in MEDICATIONS:
        end = get_end_date(med)
        status = "✅ Hoàn thành" if today > end else ("🔴 Chưa bắt đầu" if today < START_DATE else "🟢 Đang dùng")
        remaining = days_remaining(med)
        passed = days_passed(med)
        times = ", ".join(f"{s['emoji']}{s['time']}" for s in med["schedules"])
        lines.append(
            f"{med['name']}\n"
            f"  📌 {status} | Ngày {passed}/{med['duration_days']} | Còn {remaining} ngày\n"
            f"  ⏰ {times}\n"
            f"  📝 {med['note']}"
        )
        lines.append("")

    return "\n".join(lines)


def get_today_schedule() -> str:
    today = datetime.now(TZ).date()
    lines = [f"📅 <b>Lịch hôm nay – {today.strftime('%d/%m/%Y')}</b>\n"]
    has_any = False

    # Group by time
    time_slots = {}
    for med in MEDICATIONS:
        if not is_active(med):
            continue
        has_any = True
        for s in med["schedules"]:
            key = s["time"]
            if key not in time_slots:
                time_slots[key] = []
            time_slots[key].append((s["emoji"], med["name"], med["note"], med["id"]))

    if not has_any:
        return "🎉 Hôm nay không có thuốc nào cần uống!"

    for time_key in sorted(time_slots.keys()):
        lines.append(f"⏰ <b>{time_key}</b>")
        for emoji, name, note, _ in time_slots[time_key]:
            lines.append(f"  {emoji} {name} – {note}")
        lines.append("")

    return "\n".join(lines)
