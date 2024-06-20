import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("*Cześć!*\nJestem botem, który pomaga analizować rynki finansowe.\n\n*Jak działam?*\nPobieram dane "
            "z Yahoo Finance, analizuje je i na ich podstawie wyświetlam:\nTBD")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)


async def review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"tutaj będą analizowane dane o {update.message.text.split(" ")[-1]}"
    # TBD: StockAnalysis
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)


load_dotenv()
token = os.environ["API_TOKEN"]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

application = ApplicationBuilder().token(token).build()

start_handler = CommandHandler('start', start)
review_handler = CommandHandler('review', review)
r_handler = CommandHandler('r', review)

application.add_handler(start_handler)
application.add_handler(review_handler)
application.add_handler(r_handler)

application.run_polling()
