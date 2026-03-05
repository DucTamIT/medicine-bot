# 🤖 Medicine Reminder Bot

Bot Telegram nhắc lịch uống thuốc tự động. Deploy lên Railway để chạy 24/7.

## Lịch thuốc

| Thuốc | Thời lượng | Giờ nhắc |
|---|---|---|
| 💊 Thuốc xịt mũi | 14 ngày | 07:00 |
| 💨 Thuốc hít | 60 ngày | 07:00, 21:00 |
| 🧴 Rửa mặt | 30 ngày | 07:00, 21:00 |
| 💊 Thuốc uống vỉ | 30 ngày | 20:30 (2 viên) |
| 🧴 Thuốc bôi | 10 ngày | 07:15, 21:15 |
| 💊 Thuốc lẻ | 7 viên | 20:30 (1 viên) |

## Các lệnh bot

| Lệnh | Mô tả |
|---|---|
| `/start` | Chào mừng + hướng dẫn |
| `/today` | Lịch thuốc hôm nay |
| `/summary` | Tổng hợp toàn bộ lịch |
| `/status` | Trạng thái đã uống hôm nay |
| `/help` | Hướng dẫn sử dụng |

---

## 🚀 Hướng dẫn Deploy lên Railway

### Bước 1: Tạo bot Telegram
1. Mở Telegram → tìm **@BotFather**
2. Gõ `/newbot` → đặt tên → đặt username (kết thúc bằng `bot`)
3. Copy **BOT_TOKEN** được cấp

### Bước 2: Lấy Chat ID
1. Tìm **@userinfobot** trên Telegram
2. Nhắn bất kỳ → nó sẽ trả về **Chat ID** của bạn

### Bước 3: Đưa code lên GitHub
```bash
cd /đường/dẫn/tới/medicine-bot
git init
git add .
git commit -m "Initial: medicine reminder bot"
# Tạo repo mới trên github.com rồi:
git remote add origin https://github.com/YOUR_USERNAME/medicine-bot.git
git push -u origin main
```

### Bước 4: Deploy lên Railway
1. Vào **[railway.app](https://railway.app)** → đăng nhập bằng GitHub
2. Nhấn **"New Project"** → **"Deploy from GitHub repo"**
3. Chọn repo `medicine-bot`
4. Railway sẽ tự detect Python và deploy

### Bước 5: Cấu hình biến môi trường
Trong Railway dashboard → tab **Variables** → thêm:

```
BOT_TOKEN = your_token_here
CHAT_ID = your_chat_id_here
```

### Bước 6: Kiểm tra
- Tab **Deployments** → xem logs
- Mở Telegram → gõ `/start` với bot của bạn
- Bot sẽ tự nhắc đúng giờ!

---

## 🖥️ Chạy local (test)

```bash
cp .env.example .env
# Điền BOT_TOKEN và CHAT_ID vào .env

pip install -r requirements.txt
python main.py
```
