import logging
import os
import asyncio
from telegram import Update, ReactionTypeEmoji
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError, RetryAfter, Forbidden

# تنظیمات لاگ‌گیری
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.channel_post
    if not message:
        return

    emoji_to_send = "🥰"
    max_retries = 10  # افزایش تعداد تلاش‌های مجدد به ۱۰ بار

    for attempt in range(1, max_retries + 1):
        try:
            # تلاش برای ارسال ری‌اکشن
            await context.bot.set_message_reaction(
                chat_id=message.chat_id,
                message_id=message.message_id,
                reaction=[ReactionTypeEmoji(emoji_to_send)],
                is_big=False
            )
            logger.info(f"Successfully sent {emoji_to_send} to message {message.message_id} on attempt {attempt}")
            break  # در صورت موفقیت، خروج از حلقه تلاش مجدد

        except Forbidden:
            # اگر ربات دسترسی ادمین/ری‌اکشن نداشته باشد، تلاش مجدد فایده‌ای ندارد
            logger.error("Forbidden! Bot does not have permission to manage reactions in this channel.")
            break

        except RetryAfter as e:
            # اگر تلگرام ربات را محدود کند، کد دقیقا به اندازه زمان درخواستی صبر می‌کند
            wait_time = e.retry_after
            logger.warning(f"Rate limited (Flood Control). Waiting {wait_time}s... (Attempt {attempt}/{max_retries})")
            await asyncio.sleep(wait_time)

        except TelegramError as e:
            # خطاهای عمومی شبکه یا API تلگرام
            logger.error(f"Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                await asyncio.sleep(2)  # ۲ ثانیه صبر قبل از تلاش بعدی
            else:
                logger.error(f"Failed to react after {max_retries} attempts for message {message.message_id}")

def main() -> None:
    if not TOKEN:
        logger.error("TOKEN not found in environment variables!")
        return

    application = Application.builder().token(TOKEN).build()

    # فیلتر دریافت پست‌های کانال
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL & ~filters.COMMAND, handle_channel_post))

    logger.info("Bot is running with 10 retries per reaction...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

