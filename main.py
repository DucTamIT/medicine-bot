import asyncio
import logging
import signal
from bot import build_app
from scheduler import setup_scheduler, set_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("🚀 Khởi động Medicine Reminder Bot...")

    app = build_app()
    set_bot(app)

    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("✅ Scheduler đã khởi động")

    await app.initialize()
    await app.start()
    logger.info("✅ Bot đã khởi động, bắt đầu polling...")

    await app.updater.start_polling(drop_pending_updates=True)

    # Graceful shutdown
    stop_event = asyncio.Event()

    def handle_signal():
        logger.info("📴 Nhận tín hiệu dừng, đang tắt bot...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_signal)

    await stop_event.wait()

    scheduler.shutdown()
    await app.updater.stop()
    await app.stop()
    await app.shutdown()
    logger.info("👋 Bot đã tắt.")


if __name__ == "__main__":
    asyncio.run(main())
