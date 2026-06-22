#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peter Lemenkov <lemenkov@gmail.com>
# SPDX-License-Identifier: MIT

import asyncio
import logging
import os

from telegram import Update
from telegram.error import NetworkError, TimedOut
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BACKEND = os.environ.get("PICKER_BACKEND", "ollama").lower()

if BACKEND == "deepseek":
    from deepseek_picker import check_deepseek as check_backend
    from deepseek_picker import pick_phrase
else:
    from ollama_picker import check_ollama as check_backend
    from ollama_picker import pick_phrase

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
)

# Suppress noisy polling logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if isinstance(context.error, (NetworkError, TimedOut)):
        logger.debug("Network hiccup (ignored): %s", context.error)
        return
    logger.error("Unhandled exception", exc_info=context.error)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Пиши мне что угодно — я отвечу по-мужски. 😎"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Просто напиши что-нибудь. Не жди многого."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text or ""
    phrase = await pick_phrase(user_text)
    logger.debug("Responding to %s with: %s", update.effective_user.id, phrase)
    await update.message.reply_text(phrase)


def main() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_error_handler(handle_error)
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    loop.run_until_complete(check_backend())
    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
