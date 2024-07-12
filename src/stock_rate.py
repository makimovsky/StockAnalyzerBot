from ta import trend, momentum
import pandas as pd


def weekly_impulse_signal(data: pd.DataFrame, ema_short: int, macd_slow: int, macd_fast: int, macd_sign: int) -> int:
    """
    Funkcja określa tygodniowy sygnał impulse.
    :param data: DataFrame - dane do analizy z yfinance
    :param ema_short: int - okres średniej
    :param macd_slow: int - długi okres MACD
    :param macd_fast: int - krótki okres MACD
    :param macd_sign: int - okres sygnału MACD
    :return: ilość punktów
    """
    ema = trend.ema_indicator(close=data['Close'], window=ema_short)
    macd_hist = trend.macd_diff(data['Close'], window_slow=macd_slow, window_fast=macd_fast, window_sign=macd_sign)

    impulse_ema = ema.iloc[-1] - ema.iloc[-2]
    impulse_macd = macd_hist.iloc[-1] - macd_hist.iloc[-2]

    if impulse_ema > 0 and impulse_macd > 0:
        return 1
    elif impulse_ema < 0 and impulse_macd < 0:
        return 0

    pointer = -2
    while impulse_ema * impulse_macd < 0:
        impulse_ema = ema.iloc[pointer] - ema.iloc[pointer-1]
        impulse_macd = macd_hist.iloc[pointer] - macd_hist.iloc[pointer-1]
        pointer -= 1

    if impulse_ema > 0 and impulse_macd > 0:
        return 0
    elif impulse_ema < 0 and impulse_macd < 0:
        return 2


def daily_value_zone(data: pd.DataFrame, ema_short: int, ema_long: int) -> int:
    """
    Funkcja sprawdza jak cena ma się do strefy wartości.
    :param data: DataFrame - dane do analizy z yfinance
    :param ema_short: int - okres krótkiej średniej
    :param ema_long: int - okres długiej średniej
    :return: ilość punktów
    """
    ema_sh = trend.ema_indicator(close=data['Close'], window=ema_short).iloc[-1]
    ema_l = trend.ema_indicator(close=data['Close'], window=ema_long).iloc[-1]
    price = data['Close'].iloc[-1]

    if price < ema_sh and price < ema_l:
        return 2
    elif ema_sh > price > ema_l or ema_long > price > ema_sh:
        return 1
    else:
        return 0


def daily_rsi_level(data: pd.DataFrame, rsi_window: int) -> int:
    """
    Funkcja sprawdza poziom wartości przy pomocy wskaźnika RSI.
    :param data: DataFrame - dane do analizy z yfinance
    :param rsi_window: int - okres RSI
    :return: ilość punktów
    """
    data = data.loc[data.index[-1] - pd.Timedelta('182d'):]

    rsi = momentum.rsi(close=data["Close"], window=rsi_window).dropna()
    avg_rsi = rsi.mean()
    std_rsi = rsi.std()
    current_rsi = rsi.iloc[-1]

    if current_rsi < avg_rsi - std_rsi:
        return 2
    elif avg_rsi + std_rsi > current_rsi > avg_rsi - std_rsi:
        return 1
    else:
        return 0


def daily_so_level(data: pd.DataFrame, so_window: int, so_smooth_window: int) -> int:
    """
    Funkcja sprawdza poziom wartości przy pomocy Oscylatora Stochastycznego.
    :param data: DataFrame - dane do analizy z yfinance
    :param so_window: int - okres osc. stochastycznego
    :param so_smooth_window: int - okres linii sygnału w osc. stochastycznym
    :return: ilość punktów
    """
    data = data.loc[data.index[-1] - pd.Timedelta('182d'):]

    so = momentum.stoch(high=data['High'], low=data['Low'], close=data['Close'], window=so_window,
                        smooth_window=so_smooth_window).dropna()
    avg_so = so.mean()
    std_so = so.std()
    current_so = so.iloc[-1]

    if current_so < avg_so - std_so:
        return 2
    elif avg_so + std_so > current_so > avg_so - std_so:
        return 1
    else:
        return 0


def daily_adx_level(data: pd.DataFrame, adx_window: int) -> int:
    """
    Funkcja sprawdza poziom wartości przy pomocy Oscylatora Stochastycznego.
    :param data: DataFrame - dane do analizy z yfinance
    :param adx_window: okres ADX
    :return: ilość punktów
    """
    c_adx = trend.adx(high=data['High'], low=data['Low'], close=data['Close'], window=adx_window).iloc[-1]
    dipos = trend.adx_pos(high=data['High'], low=data['Low'], close=data['Close'], window=adx_window).iloc[-1]
    dineg = trend.adx_neg(high=data['High'], low=data['Low'], close=data['Close'], window=adx_window).iloc[-1]

    if dipos > c_adx > dineg:
        return 2
    elif c_adx < dipos and c_adx < dineg:
        return 1
    else:
        return 0
