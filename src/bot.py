import logging
import os
from datetime import datetime

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from markups import *
from stock_analysis import year_cycle_graph, rsi_so_price, adx, macd, price_atr_ad, moving_averages


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Funckja obsługuje komendę /start.
    :param update: Obiekt klasy Update, który reprezentuje bieżące zdarzenie w Telegramie.
    :param context: Obiekt klasy Context, który zawiera informacje kontekstowe dotyczące bieżącego stanu bota.
    :return: None
    """
    text = ("*Cześć!*\nJestem botem, który pomaga analizować rynki finansowe.\n\n*Jak działam?*\nPobieram dane "
            "z Yahoo Finance i na ich podstawie wyświetlam wykresy oraz wartości wskaźników.\nWpisz /help, aby uzyskać "
            "informacje o dostępnych komendach.")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)

    return


async def review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Funkcja obsługuje analize rynków finansowych.
    :param update: Obiekt klasy Update, który reprezentuje bieżące zdarzenie w Telegramie.
    :param context: Obiekt klasy Context, który zawiera informacje kontekstowe dotyczące bieżącego stanu bota.
    :return: None
    """
    chat = update.effective_chat.id

    intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '1d', '1wk', '1mo']

    periods = {
        '1d': intervals[0:3],
        '5d': intervals[2:4],
        '1mo': intervals[4:6],
        '6mo': intervals[6:7],
        '1y': intervals[6:8],
        '2y': intervals[6:8],
        '5y': intervals[7:],
        '10y': intervals[8:],
    }

    periods_timedeltas = {
        '1d': '1d',
        '5d': '5d',
        '1mo': '30d',
        '6mo': '182d',
        '1y': '365d',
        '2y': '730d',
        '5y': '1826d',
        '10y': '3652d',
    }

    try:
        symbol = update.message.text.split(" ")[1]
    except IndexError:
        err_msg = f"Błąd - podaj symbol. Aby uzyskać więcej pomocy wpisz /help."
        await context.bot.send_message(chat_id=chat, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return
    try:
        period = update.message.text.split(" ")[2]
    except IndexError:
        period = "1y"

    if period not in periods:
        period_keys = str(list(periods.keys())).replace("'", "")
        err_msg = f"Błąd - dostępne okresy czasu: {period_keys}"
        await context.bot.send_message(chat_id=chat, text=err_msg,
                                       parse_mode=ParseMode.MARKDOWN)
        return

    try:
        interval = update.message.text.split(" ")[3]
    except IndexError:
        interval = periods.get(period)[0]

    if interval not in intervals:
        interval_keys = str(intervals).replace("'", "")
        err_msg = f"Błąd - dostępne interwały: {interval_keys}"
        await context.bot.send_message(chat_id=chat, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    if interval not in periods.get(period):
        period_intervals = str(periods.get(period)).replace("'", "")
        err_msg = f"Błąd - dostępne interwały dla okresu {period}: {period_intervals}"
        await context.bot.send_message(chat_id=chat, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    match interval:
        case '1m' | '1d' | '1wk' | '1mo':
            data = yf.download(symbol, period='max', interval=interval)
        case '2m' | '5m' | '15m' | '30m':
            data = yf.download(symbol, start=datetime.now() - pd.Timedelta('59d'), interval=interval)
        case '60m':
            data = yf.download(symbol, period='2y', interval=interval)
        case _:
            err_msg = f"Błąd!"
            await context.bot.send_message(chat_id=chat, text=err_msg, parse_mode=ParseMode.MARKDOWN)
            return

    if data.empty:
        err_msg = f"Błąd - Brak danych o *{symbol}*. Upewnij się, że podajesz istniejący symbol giełdowy."
        await context.bot.send_message(chat_id=chat, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    start_date = data.index[-1] - pd.Timedelta(periods_timedeltas.get(period))

    # wykres slupkowy oraz kanały ATR
    try:
        chart = price_atr_ad(data=data, mode=mode, start=start_date, atr_window=config['atr_window'],
                             atr_ema_window=config['atr_ema_window'])
    except ValueError:
        err_msg = f"Błąd - sprawdź, czy spółka istnieje przez podany okres czasu."
        await context.bot.send_message(chat_id=chat, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return
    await context.bot.send_photo(chat_id=chat, photo=chart,
                                 caption='Wykres słupkowy cen + kanały ATR + wskaźnik akumulacji/dystrybucji')

    # srednie kroczace
    chart = moving_averages(data=data, mode=mode, start=start_date, short_window=config['ema_short'],
                            long_window=config['ema_long'])
    await context.bot.send_photo(chat_id=chat, photo=chart,
                                 caption='Wykres średnich kroczących')

    # RSI/SO/Cena
    chart = rsi_so_price(data=data, mode=mode, start=start_date, rsi_window=config['rsi_window'],
                         so_window=config['so_window'], so_smooth_window=config['so_smooth_window'])
    await context.bot.send_photo(chat_id=chat, photo=chart, caption='RSI + Osc. stochastyczny',
                                 parse_mode=ParseMode.MARKDOWN)

    # cykle roczne
    if period in list(periods.keys())[6:]:
        chart = year_cycle_graph(data=data, mode=mode, start=start_date)
        await context.bot.send_photo(chat_id=chat, photo=chart,
                                     caption='Wykres możliwych cykli rocznych')

    # ADX
    chart = adx(data=data, mode=mode, start=start_date, adx_window=config['adx_window'])
    await context.bot.send_photo(chat_id=chat, photo=chart, caption='ADX - wskaźnik trendu')

    # MACD
    chart = macd(data=data, mode=mode, start=start_date, macd_slow=config['macd_slow'], macd_fast=config['macd_fast'],
                 macd_sign=config['macd_sign'])
    await context.bot.send_photo(chat_id=chat, photo=chart, caption='Wskaźnik MACD',
                                 reply_markup=main_markup)

    return


async def help_func(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Funckja obsługuje pomoc.
    :param update: Obiekt klasy Update, który reprezentuje bieżące zdarzenie w Telegramie.
    :param context: Obiekt klasy Context, który zawiera informacje kontekstowe dotyczące bieżącego stanu bota.
    :return: None
    """
    help_text = ('*Dostępne komendy:*\n */review (/r) [symbol] [okres] [interwał]*\n\n  *Opis:*\n   Komenda służy do '
                 'wyświetlania danych\n   o podanym symbolu w podanym\n   okresie z podanym interwałem.\n\n  '
                 '*Parametry:*\n   _symbol_: Symbol giełdowy\n   _okres_: Okres danych\n   _interwał_: Interwał '
                 'danych\n\n  *Przykładowe użycie:*\n   /r aapl 5y 1wk - wyświetlenie danych o\n   AAPL z ostatnich 5 '
                 'lat z jednostką osi\n   czasu 1 tydzień.\n\n\n */ihelp (/ih) [atr/średnie/rsi/os/\n               '
                 '         /adx/macd]*\n\n  *Opis:*\n   Komenda służy do wyświetlenia\n   pomocy dotyczącej '
                 'interpretacji\n   wysyłanych przez bota wykresów i\n   danych.\n\n\n */help (/h)*\n\n  *Opis:*\n   '
                 'Komenda służy do wyświetlenia\n   dostępnych komend.\n\n\n */mode (/m) [light/dark/darkblue]*\n\n  '
                 '*Opis:*\n   Komenda służy do zmiany motywu\n   wyświetlanych wykresów.')

    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode=ParseMode.MARKDOWN)

    return


async def ihelp_func(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Funkcja obsługuje pomoc w interpretacji wskaźników.
    :param update: Obiekt klasy Update, który reprezentuje bieżące zdarzenie w Telegramie.
    :param context: Obiekt klasy Context, który zawiera informacje kontekstowe dotyczące bieżącego stanu bota.
    :return: None
    """
    chat = update.effective_chat.id

    atr_help = ('*Wskaźnik ATR* - wkaźnik średniej rzeczywistej zmienności. Wskaźnik ten jest pomocny przy wyznaczaniu '
                'poziomów docelowych oraz poziomów stop loss. Stop loss powinien znajdować się w oddaleniu od poziomu '
                'wejścia przynajmniej o 1 ATR w dół. Po otwarciu transakcji, zyski można realizować przy poziomach '
                '1, 2 lub 3 ATR w górę. Warto pamiętać jednak, że rynek znajdujący się w okolicach 3 ATR jest w dużym '
                'stopniu wykupiony lub wyprzedany, więc z dużym prawdopodobieństwem można spodziewać się korekty lub '
                'odwrócenia trendu.')

    ad_help = ('*Wskaźnik A/D* - wkaźnik akumulacji/dystrybucji. Wskaźnik ten jest pomocny przy śledzeniu wolumenu. '
               'Dywergencje między wskaźnikiem A/D, a ceną dają bardzo silne sygnały transakcyjne.')

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
                ' że ADX znajdujący się poniżej dwóch linii +DI oraz -DI oznacza brak trendu. W momencie, gdy ADX '
                'przebija jedną z linii kierunkowych, jest to sygnał rozpoczęcia nowego trendu. Trend ten jest '
                'wzrostowy, jeżeli linia +DI znajduje się nad linią -DI lub spadkowy w odwrotnym przypadku. Jeżeli ADX '
                'osiąga poziom powyżej obu linii kierunkowych, jest to oznaka, że za niedługo prawdopodobnie pojawi się'
                ' korekta lub odwrócenie trendu.')

    macd_help = ('*MACD* - sygnał pojawia się, gdy szybsza linia MACD przecina wolniejszą linie sygnału. Przecięcie '
                 'MACD od dołu jest sygnałem kupna, a od góry - sygnałem sprzedaży. Czytelniejszym wykresem jest wykres'
                 ' słupkowy, na którym łatwiej można zaobserwować odległość linii od siebie. Ważnym sygnałem dawanym '
                 'przez MACD jest dywergencja między histogramem MACD, a ceną. Dywergencja występuje, jeżeli nowy dołek'
                 ' lub szczyt cenowy nie jest potwierdzony przez nowy dołek lub szczyt histogramu MACD. Ważnym aspektem'
                 ' jest to, że histogram MACD pomiędzy dwoma szczytami lub dołkami musi przeciąć linię 0. Oznacza to, '
                 'że jeżeli ceny wyznaczyły nowy szczyt, a histogram nie, ale pomiędzy dwoma szczytami histogram nie '
                 'przeszedł przez linię 0, to nie możemy mówić o dywergencji.')

    ihelp_text = f'{atr_help}\n\n{ad_help}\n\n{ma_help}\n\n{rsi_help}\n\n{so_help}\n\n{adx_help}\n\n{macd_help}'

    try:
        help_w = update.message.text.split(" ")[1]
    except IndexError:
        await context.bot.send_message(chat_id=chat, text=ihelp_text, parse_mode=ParseMode.MARKDOWN)
        return

    match help_w:
        case 'atr':
            await context.bot.send_message(chat_id=chat, text=atr_help, parse_mode=ParseMode.MARKDOWN)
        case 'a/d':
            await context.bot.send_message(chat_id=chat, text=ad_help, parse_mode=ParseMode.MARKDOWN)
        case 'średnie':
            await context.bot.send_message(chat_id=chat, text=ma_help, parse_mode=ParseMode.MARKDOWN)
        case 'rsi':
            await context.bot.send_message(chat_id=chat, text=rsi_help, parse_mode=ParseMode.MARKDOWN)
        case'os':
            await context.bot.send_message(chat_id=chat, text=so_help, parse_mode=ParseMode.MARKDOWN)
        case 'adx':
            await context.bot.send_message(chat_id=chat, text=adx_help, parse_mode=ParseMode.MARKDOWN)
        case 'macd':
            await context.bot.send_message(chat_id=chat, text=macd_help, parse_mode=ParseMode.MARKDOWN)
        case _:
            err_msg = f'Błąd - brak pomocy dla *{help_w}*. Aby uzyskać więcej pomocy wpisz /help.'
            await context.bot.send_message(chat_id=chat, text=err_msg, parse_mode=ParseMode.MARKDOWN)

    return


async def mode_func(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Funkcja obsługuje zmianę motywu przez użytkownika.
    :param update: Obiekt klasy Update, który reprezentuje bieżące zdarzenie w Telegramie.
    :param context: Obiekt klasy Context, który zawiera informacje kontekstowe dotyczące bieżącego stanu bota.
    :return: None
    """
    chat = update.effective_chat.id

    global mode

    try:
        desired_mode = update.message.text.split(" ")[1]
    except IndexError:
        err_msg = 'Błąd - podaj motyw. Aby uzyskać więcej pomocy wpisz /help.'
        await context.bot.send_message(chat_id=chat, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    if desired_mode in list(modes.keys()):
        mode = modes[desired_mode]
        config['mode'] = desired_mode
        with open('config.yml', 'w') as cfg_file_update:
            yaml.dump(config, cfg_file_update, default_flow_style=False)
        msg = f'Pomyślnie zmieniono motyw na *{desired_mode}*'
        await context.bot.send_message(chat_id=chat, text=msg, parse_mode=ParseMode.MARKDOWN)
    else:
        err_msg = f'Błąd - brak motywu o nazwie *{desired_mode}*. Aby uzyskać więcej pomocy wpisz /help.'
        await context.bot.send_message(chat_id=chat, text=err_msg, parse_mode=ParseMode.MARKDOWN)

    return


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Funckja obsługuje wciskane przez użytkownika przyciski.
    :param update: Obiekt klasy Update, który reprezentuje bieżące zdarzenie w Telegramie.
    :param context: Obiekt klasy Context, który zawiera informacje kontekstowe dotyczące bieżącego stanu bota.
    :return: None
    """
    chat = update.effective_chat.id
    query = update.callback_query
    global mode, settings_value

    match query.data:
        case 'settings':
            await context.bot.send_message(chat_id=chat, text='*Ustawienia*', parse_mode=ParseMode.MARKDOWN,
                                           reply_markup=settings_markup)
        case 'set_return':
            await query.edit_message_text(text='*Ustawienia*', parse_mode=ParseMode.MARKDOWN,
                                          reply_markup=settings_markup)
        case 'cb_mode':
            await query.edit_message_text(text='*Wybierz motyw*', parse_mode=ParseMode.MARKDOWN,
                                          reply_markup=modes_markup)
        case m if m in modes:
            mode = modes[m]
            config['mode'] = m
            with open('config.yml', 'w') as cfg_file_update:
                yaml.dump(config, cfg_file_update, default_flow_style=False)
            msg = f'Pomyślnie zmieniono motyw na *{m}*'
            await query.edit_message_text(text=msg, parse_mode=ParseMode.MARKDOWN)
        case 'atr':
            settings_atr = (f'*Ustawienia ATR*\nOkres średniej: {config["atr_ema_window"]}\nOkres ATR: '
                            f'{config["atr_window"]}')
            await query.edit_message_text(text=settings_atr, parse_mode=ParseMode.MARKDOWN, reply_markup=atr_markup)
        case 'ma':
            settings_ma = (f'*Ustawienia średnich*\nOkres krótkiej średniej: {config["ema_short"]}\nOkres długiej '
                           f'średniej: {config["ema_long"]}')
            await query.edit_message_text(text=settings_ma, parse_mode=ParseMode.MARKDOWN, reply_markup=ma_markup)
        case 'rsi':
            settings_rsi = f'*Ustawienia RSI*\nOkres RSI: {config["rsi_window"]}'
            await query.edit_message_text(text=settings_rsi, parse_mode=ParseMode.MARKDOWN, reply_markup=rsi_markup)
        case 'so':
            settings_so = (f'*Ustawienia osc. stochastycznego*\nOkres osc. stochastycznego: {config["so_window"]}'
                           f'\nOkres sygnału: {config["so_smooth_window"]}')
            await query.edit_message_text(text=settings_so, parse_mode=ParseMode.MARKDOWN, reply_markup=so_markup)
        case 'adx':
            settings_adx = f'*Ustawienia ADX*\nOkres ADX: {config["adx_window"]}'
            await query.edit_message_text(text=settings_adx, parse_mode=ParseMode.MARKDOWN, reply_markup=adx_markup)
        case 'macd':
            settings_macd = (f'*Ustawienia MACD*\nKrótki okres MACD: {config["macd_fast"]}\nDługi okres MACD: '
                             f'{config["macd_slow"]}\nOkres sygnału MACD: {config["macd_sign"]}')
            await query.edit_message_text(text=settings_macd, parse_mode=ParseMode.MARKDOWN, reply_markup=macd_markup)
        case sv if sv in config:
            manage_handlers(remove=True)
            settings_value = sv
            await query.edit_message_text(text='Podaj okres')

    return


async def settings_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Funkcja obsługuje zmianę ustawień w configu.
    :param update: Obiekt klasy Update, który reprezentuje bieżące zdarzenie w Telegramie.
    :param context: Obiekt klasy Context, który zawiera informacje kontekstowe dotyczące bieżącego stanu bota.
    :return: None
    """
    global config

    try:
        arg = int(update.message.text)
    except ValueError:
        err_msg = f'Błąd - Podaj prawidłową liczbę.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    if arg > 300 or arg < 3:
        err_msg = f'Błąd - Okres nie może być dłuższy niż 300 i krótszy niż 3.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)
        return

    config[settings_value] = arg

    with open('config.yml', 'w') as cfg_file_update:
        yaml.dump(config, cfg_file_update, default_flow_style=False)
    msg = f'Pomyślnie zmieniono okres na *{arg}*'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.MARKDOWN)
    manage_handlers()

    return


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Funkcja obsługuje nieznane komendy.
    :param update: Obiekt klasy Update, który reprezentuje bieżące zdarzenie w Telegramie.
    :param context: Obiekt klasy Context, który zawiera informacje kontekstowe dotyczące bieżącego stanu bota.
    :return: None
    """
    err_msg = 'Błąd. Aby uzyskać więcej pomocy wpisz \n/help.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=err_msg, parse_mode=ParseMode.MARKDOWN)

    return


def manage_handlers(remove: bool = False) -> None:
    """
    Funkcja służy do włączania i wyłączania handlerów.
    :param remove: True - wyłączenie / False - włączenie
    :return: None
    """
    if remove:
        application.remove_handler(start_handler)
        application.remove_handler(review_handler)
        application.remove_handler(help_handler)
        application.remove_handler(ihelp_handler)
        application.remove_handler(mode_handler)
        application.remove_handler(unknown_handler)
        application.add_handler(settings_handler)

        return

    application.remove_handler(settings_handler)
    application.add_handler(start_handler)
    application.add_handler(review_handler)
    application.add_handler(help_handler)
    application.add_handler(ihelp_handler)
    application.add_handler(mode_handler)
    application.add_handler(unknown_handler)

    return


if __name__ == '__main__':
    load_dotenv()
    token = os.environ["BOT_TOKEN"]

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    with open('modes.yml', 'r') as file:
        modes = yaml.safe_load(file)

    with open('config.yml', 'r') as cfg_file:
        config = yaml.safe_load(cfg_file)

    mode = modes[config['mode']]
    settings_value = None

    application = ApplicationBuilder().token(token).read_timeout(120).build()

    start_handler = CommandHandler('start', start)
    review_handler = CommandHandler(['review', 'r'], review)
    help_handler = CommandHandler(['help', 'h'], help_func)
    ihelp_handler = CommandHandler(['ihelp', 'ih'], ihelp_func)
    mode_handler = CommandHandler(['mode', 'm'], mode_func)
    callback_handler = CallbackQueryHandler(button)
    settings_handler = MessageHandler(filters.TEXT, settings_manager)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(callback_handler)

    manage_handlers()

    application.run_polling()
