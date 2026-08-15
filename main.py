import logging
import os
import asyncio
from telegram import Update, ReactionTypeEmoji
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError, RetryAfter, Forbidden

# تنظیمات لاگ‌گیری دقیق
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
    max_retries = 10

    for attempt in range(1, max_retries + 1):
        try:
            await context.bot.set_message_reaction(
                chat_id=message.chat_id,
                message_id=message.message_id,
                reaction=[ReactionTypeEmoji(emoji_to_send)],
                is_big=False
            )
            logger.info(f"موفقیت: ری‌اکشن {emoji_to_send} روی پیام {message.message_id} ثبت شد.")
            break

        except Forbidden:
            logger.error("خطا: ربات دسترسی Manage Reactions در کانال را ندارد!")
            break

        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)

        except TelegramError as e:
            logger.error(f"خطا در تلاش {attempt}: {e}")
            if attempt < max_retries:
                await asyncio.sleep(1.5)
            else:
                logger.error("ثبت ری‌اکشن ناموفق بود.")

def main() -> None:
    if not TOKEN:
        logger.error("توکن یافت نشد!")
        return

    application = Application.builder().token(TOKEN).build()

    # فیلتر دقیق برای دریافت پست‌های جدید کانال
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL & ~filters.COMMAND, handle_channel_post))

    logger.info("ربات روشن شد و منتظر پست‌های جدید است...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
