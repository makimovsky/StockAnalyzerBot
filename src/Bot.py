import logging
import os
import yfinance as yf
import yaml

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from StockAnalysis import year_cycle_graph, rsi_so_price, adx, macd, price_bollinger, moving_averages


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("*Cześć!*\nJestem botem, który pomaga analizować rynki finansowe.\n\n*Jak działam?*\nPobieram dane "
            "z Yahoo Finance i na ich podstawie wyświetlam wykresy oraz wartości wskaźników. Wpisz /help, aby uzyskać "
            "więcej informacji.")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)

    return


async def review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global mode
    intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1d', '5d', '1wk', '1mo']

    periods = {
        '1d': intervals[0:3],
        '5d': intervals[0:6],
        '1mo': intervals[3:8],
        '6mo': intervals[7:8],
        '1y': intervals[7:10],
        '2y': intervals[7:10],
        '5y': intervals[7:],
        '10y': intervals[7:],
    }

    try:
        symbol = update.message.text.split(" ")[1]
    except IndexError:
        err_msg = f"Błąd - podaj symbol. Aby uzyskać więcej pomocy wpisz /help."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return
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
        err_msg = f"Błąd - Brak danych o *{symbol}*. Upewnij się, że podajesz istniejący symbol giełdowy."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    # wykres swiecowy ze wstegami Bollingera
    chart = price_bollinger(data, mode)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart,
                                 caption='Wykres świecowy cen + wstęgi Bollingera')

    # srednie kroczace
    chart = moving_averages(data, mode)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart,
                                 caption='Wykres średnich kroczących')

    # RSI/SO/Cena
    values = rsi_so_price(data, mode)

    stats = (f"*RSI:*\n\tAktualna wartość: {values[2]}\n\tŚrednia: {values[0]}\n\tOdchylenie: {values[1]}"
             f"\n\n*Oscylator stochastyczny:*\n\tAktualna wartość: {values[5]}\n\tŚrednia: {values[3]}"
             f"\n\tOdchylenie: {values[4]}")
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=values[6], caption=stats,
                                 parse_mode=ParseMode.MARKDOWN)

    # cykle roczne
    if period in list(periods.keys())[6:]:
        chart = year_cycle_graph(data, mode)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart,
                                     caption='Wykres możliwych cykli rocznych')

    # ADX
    chart = adx(data, mode)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart, caption='ADX - wskaźnik trendu')

    # MACD
    chart = macd(data, mode)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart, caption='Wskaźnik MACD')

    return


async def help_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = ('*Dostępne komendy:*\n */review (/r) [symbol] [okres] [interwał]*\n\n  *Opis:*\n   Komenda służy do '
                 'wyświetlania danych\n   o podanym symbolu w podanym\n   okresie z podanym interwałem.\n\n  '
                 '*Parametry:*\n   _symbol_: Symbol giełdowy\n   _okres_: Okres danych\n   _interwał_: Interwał '
                 'danych\n\n  *Przykładowe użycie:*\n   /r aapl 5y 1wk - wyświetlenie danych o\n   AAPL z ostatnich 5 '
                 'lat z jednostką osi\n   czasu 1 tydzień.\n\n\n */ihelp (/ih) [bollinger/średnie/rsi/\n               '
                 '         /os/adx/macd]*\n\n  *Opis:*\n   Komenda służy do wyświetlenia\n   pomocy dotyczącej '
                 'interpretacji\n   wysyłanych przez bota wykresów i\n   danych.\n\n\n */help (/h)*\n\n  *Opis:*\n   '
                 'Komenda służy do wyświetlenia\n   dostępnych komend.\n\n\n */mode (/m) [light/dark]*\n\n  *Opis:*'
                 '\n   Komenda służy do zmiany motywu\n   wyświetlanych wykresów.')

    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode=ParseMode.MARKDOWN)


async def ihelp_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bollinger_help = ('*Wstęgi Bollingera* - odległość górnej wstęgi od dolnej jest miarą zmienności rynku. Gdy '
                      'zmienność rynku jest duża, wówczas dobrą strategią jest sprzedawanie przy górnej wstędze, a '
                      'kupowanie przy dolnej. Wąska wstęga oznacza spokojny rynek w stanie konsolidacji, a szeroka - '
                      'rynek aktywny.')

    ma_help = ('*Średnie kroczące* - sygnał kupna pojawia się, gdy krótsza średnia przecina od dołu dłuższą średnią,'
               'natomiast sygnał sprzedaży - gdy krótsza średnia przecina dłuższą od góry. Czytelniejszym wykresem jest'
               ' wykres słupkowy, na którym łatwiej można zaobserwować odległość średnich od siebie.')

    rsi_help = ('*RSI* - wskaźnik siły względnej. RSI daje sygnały dwóch rodzajów. Są to dywergencje między RSI a ceną '
                'oraz poziomy wykupienia i wyprzedania RSI. Dywergencje byka lub niedźwiedzia pomiędzy RSI a cenami '
                'dają najsilniejsze sygnały kupna i sprzedaży. Pojawiają się, gdy RSI nie potwierdza nowego dołka lub '
                'nowego szczytu (cena osiąga nowy dołek lub szczyt, a RSI nie). Poziomy wykupienia i wyprzedania RSI '
                'dają informacje o tym, czy rynek jest wykupiony lub wyprzedany. Jeżeli RSI jest ponad linią wykupienia'
                ' oznacza to, że za niedługo mogą nastąpić spadki (korekta). Wyprzedanie jest odwrotną sytuacją. '
                'Domyślnie za poziom wykupienia uznaje się poziom >70, a za poziom wyprzedania <30, jednak bot wykreśla'
                ' linie wykupienia i wyprzedania na poziomach średnia wartość RSI +- odchylenie RSI z podanego okresu '
                'tak, aby dostosować poziomy do danej spółki.')

    so_help = ('*Oscylator stochastyczny* - ocenia impet rynku, bada relacje pomiędzy każdą ceną zamknięcia i ostatnim '
               'zakresem wahań cen. Przecięcia linii sygnału z linią oscylatora w obszarach wykupienia lub wyprzedania '
               'są sygnałami kupna lub sprzedaży. Warto również łączyć ten oscylator z RSI.')

    adx_help = ('*ADX* - wskaźnik trendu. Rosnąca linia ADX oznacza, że na rynku dominuje wyraźny trend. Można przyjąć,'
                ' że wybicie ponad poziom 20 jest potwierdzeniem rozpoczęcia trendu, a wybicie ponad poziom 40 może '
                'oznaczać zbliżający się koniec trendu lub korektę.')

    macd_help = ('*MACD* - sygnał pojawia się, gdy szybsza linia MACD przecina wolniejszą linie sygnału. Przecięcie '
                 'MACD od dołu jest sygnałem kupna, a od góry - sygnałem sprzedaży. Czytelniejszym wykresem jest wykres'
                 ' słupkowy, na którym łatwiej można zaobserwować odległość linii od siebie.')

    ihelp_text = f'{bollinger_help}\n\n{ma_help}\n\n{rsi_help}\n\n{so_help}\n\n{adx_help}\n\n{macd_help}'

    try:
        help_w = update.message.text.split(" ")[1]
    except IndexError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=ihelp_text, parse_mode=ParseMode.MARKDOWN)
        return

    if help_w == 'bollinger':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=bollinger_help,
                                       parse_mode=ParseMode.MARKDOWN)
    elif help_w == 'średnie':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=ma_help, parse_mode=ParseMode.MARKDOWN)
    elif help_w == 'rsi':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=rsi_help, parse_mode=ParseMode.MARKDOWN)
    elif help_w == 'os':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=so_help, parse_mode=ParseMode.MARKDOWN)
    elif help_w == 'adx':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=adx_help, parse_mode=ParseMode.MARKDOWN)
    elif help_w == 'macd':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=macd_help, parse_mode=ParseMode.MARKDOWN)
    else:
        err_msg = f'Błąd - brak pomocy dla *{help_w}*. Aby uzyskać więcej pomocy wpisz /help.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)

    return


async def mode_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global modes, mode
    try:
        desired_mode = update.message.text.split(" ")[1]
    except IndexError:
        err_msg = 'Błąd - podaj motyw. Aby uzyskać więcej pomocy wpisz /help.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    if desired_mode in list(modes.keys()):
        mode = modes[desired_mode]
        msg = f'Pomyślnie zmieniono motyw na *{desired_mode}*'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.MARKDOWN)
    else:
        err_msg = f'Błąd - brak motywu o nazwie *{desired_mode}*. Aby uzyskać więcej pomocy wpisz /help.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)

    return


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    err_msg = 'Błąd. Aby uzyskać więcej pomocy wpisz \n/help.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)

    return


if __name__ == '__main__':
    load_dotenv()
    token = os.environ["API_TOKEN"]

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    with open('modes.yml', 'r') as file:
        modes = yaml.safe_load(file)

    mode = modes['dark']

    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler('start', start)
    review_handler = CommandHandler(['review', 'r'], review)
    help_handler = CommandHandler(['help', 'h'], help_func)
    ihelp_handler = CommandHandler(['ihelp', 'ih'], ihelp_func)
    mode_handler = CommandHandler(['mode', 'm'], mode_func)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(review_handler)
    application.add_handler(help_handler)
    application.add_handler(ihelp_handler)
    application.add_handler(mode_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
