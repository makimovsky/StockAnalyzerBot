import logging
import os
import yfinance as yf

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from StockAnalysis import year_cycle_graph, rsi_so_price, adx, macd, price_bollinger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("*Cześć!*\nJestem botem, który pomaga analizować rynki finansowe.\n\n*Jak działam?*\nPobieram dane "
            "z Yahoo Finance i na ich podstawie wyświetlam wykresy oraz wartości wskaźników.")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)


async def review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1d', '5d', '1wk', '1mo', '3mo']

    periods = {
        '1d': intervals[0:3],
        '5d': intervals[0:6],
        '1mo': intervals[3:8],
        '6mo': intervals[7:8],
        '1y': intervals[7:10],
        '2y': intervals[7:10],
        '5y': intervals[7:11],
        '10y': intervals[7:],
    }

    symbol = update.message.text.split(" ")[1]
    try:
        period = update.message.text.split(" ")[2]
    except IndexError:
        period = "1y"
    try:
        interval = update.message.text.split(" ")[3]
    except IndexError:
        interval = periods.get(period)[0]

    if period not in periods:
        period_keys = str(list(periods.keys())).replace("'", "")
        err_msg = f"Błąd - dostępne okresy czasu: {period_keys}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    if interval not in intervals:
        interval_keys = str(intervals).replace("'", "")
        err_msg = f"Błąd - dostępne interwały: {interval_keys}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    if interval not in periods.get(period):
        period_intervals = str(periods.get(period)).replace("'", "")
        err_msg = f"Błąd - dostępne interwały dla okresu {period}: {period_intervals}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    data = yf.download(symbol, period=period, interval=interval)

    if data.empty:
        err_msg = f"Błąd - Brak danych o *{symbol}*"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    # wykres swiecowy ze wstegami Bollingera
    chart = price_bollinger(data)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart)

    # RSI/SO/Cena
    values = rsi_so_price(data)

    stats = (f"*RSI:*\n\tAktualna wartość: {values[2]}\n\tŚrednia: {values[0]}\n\tOdchylenie: {values[1]}"
             f"\n\n*Oscylator stochastyczny:*\n\tAktualna wartość: {values[5]}\n\tŚrednia: {values[3]}"
             f"\n\tOdchylenie: {values[4]}")
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=values[6])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=stats, parse_mode=ParseMode.MARKDOWN)

    # cykle roczne
    if period in list(periods.keys())[6:]:
        chart = year_cycle_graph(data)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart)

    # ADX
    chart = adx(data)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart)

    # MACD
    chart = macd(data)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart)


if __name__ == '__main__':
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
