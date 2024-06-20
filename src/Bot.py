import logging
import os
import datetime
import yfinance as yf

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from StockAnalysis import year_cycle_graph, rsi_so_price


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("*Cześć!*\nJestem botem, który pomaga analizować rynki finansowe.\n\n*Jak działam?*\nPobieram dane "
            "z Yahoo Finance, analizuje je i na ich podstawie wyświetlam:\nTBD")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)


async def review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.split(" ")[-1]

    year = datetime.datetime.now().year - 5
    data = yf.download(symbol, start=f"{year}-01-01")

    if data.empty:
        err_msg = f"Błąd - Brak danych o *{symbol}*"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    # RSI/SO/Price chart
    values = rsi_so_price(data)

    stats = (f"*RSI:*\n\tAktualna wartość: {values[2]}\n\tŚrednia: {values[0]}\n\tOdchylenie: {values[1]}"
             f"\n\n*Oscylator stochastyczny:*\n\tAktualna wartość: {values[5]}\n\tŚrednia: {values[3]}"
             f"\n\tOdchylenie: {values[4]}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=stats, parse_mode=ParseMode.MARKDOWN)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo="../resources/rop.png")

    # year cycle chart
    year_cycle_graph(data)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo="../resources/ycycle.png")


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
