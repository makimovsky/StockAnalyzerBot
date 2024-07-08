import pandas as pd
import matplotlib.pyplot as plt
from ta import trend, momentum, volatility, volume
from io import BytesIO
import mplfinance as mpf


def set_chart_style(fig: plt.Figure, axes: list, mode: dict) -> tuple:
    """
    Funkcja ustawia motyw na wykresie.
    :param fig: matplotlib Figure
    :param axes: lista Ax
    :param mode: dict - motyw wykresów
    :return: tuple
    """
    fig.patch.set_facecolor(mode['face'])
    for ax in axes:
        ax.set_facecolor(mode['face'])
        ax.spines['top'].set_color(mode['edge'])
        ax.spines['bottom'].set_color(mode['edge'])
        ax.spines['left'].set_color(mode['edge'])
        ax.spines['right'].set_color(mode['edge'])
        ax.tick_params(axis='x', colors=mode['axes_label'])
        ax.tick_params(axis='y', colors=mode['axes_label'])
        ax.yaxis.label.set_color(mode['axes_label'])
        ax.xaxis.label.set_color(mode['axes_label'])
        ax.title.set_color(mode['title'])
        ax.grid(color=mode['grid'], linestyle='--')
    return fig, axes


def save_plot_to_buffer() -> BytesIO:
    """
    Funkcja zapisuje wykres do bufora.
    :return: BytesIO
    """
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()
    plt.close()
    return buffer


def year_cycle_graph(data: pd.DataFrame, mode: dict, start: pd.Timestamp) -> BytesIO:
    """
    Funkcja tworzy wykres możliwych cykli rocznych.
    :param data: DataFrame - dane do analizy z yfinance
    :param mode: dict - motyw wykresów
    :param start: Timestamp - data rozpoczęcia wykresu
    :return: BytesIO
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    fig, axes = set_chart_style(fig, [ax], mode)
    ax = axes[0]

    p_start = pd.Timestamp(year=int(start.year), month=1, day=1)
    data = data.loc[p_start:]

    for year in data.index.year.unique():
        data_year = data[data.index.year == year]["Close"]
        data_year = data_year / data_year.max()
        data_year.index = data_year.index.strftime('%m-%d')
        data_year.plot(ax=ax, label=str(year))

    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    leg = ax.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    plt.tight_layout()
    return save_plot_to_buffer()


def rsi_so_price(data: pd.DataFrame, mode: dict, start: pd.Timestamp, rsi_window: int, so_window: int,
                 so_smooth_window: int) -> BytesIO:
    """
    Funkcja tworzy wykres ceny do RSI oraz Osc. stochastycznego.
    :param data: DataFrame - dane do analizy z yfinance
    :param mode: dict - motyw wykresów
    :param start: Timestamp - data rozpoczęcia wykresu
    :param rsi_window: int - okres RSI
    :param so_window: int - okres osc. stochastycznego
    :param so_smooth_window: int - okres linii sygnału w osc. stochastycznym
    :return: BytesIO
    """
    # RSI
    rsi = momentum.rsi(close=data["Close"], window=rsi_window).dropna()
    rsi = rsi.loc[start:]

    avg_rsi = rsi.mean()
    std_rsi = rsi.std()

    # Stochastics Oscilator
    so = momentum.stoch(high=data['High'], low=data['Low'], close=data['Close'], window=so_window,
                        smooth_window=so_smooth_window).dropna()
    so_signal = momentum.stoch_signal(high=data['High'], low=data['Low'], close=data['Close'], window=so_window,
                                      smooth_window=so_smooth_window).dropna()
    so = so.loc[start:]
    so_signal = so_signal.loc[start:]

    avg_so = so.mean()
    std_so = so.std()

    # chart
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig, axes = set_chart_style(fig, [ax1, ax2, ax3], mode)

    ax1, ax2, ax3 = axes

    ax1.plot(data['Close'].loc[rsi.index[0]:rsi.index[-1]], color=mode['price'], label='Cena')
    ax1.set_ylabel('Cena')
    leg = ax1.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    ax2.plot(rsi, color=mode['rsi'], label="RSI")
    ax2.axhline(y=avg_rsi + std_rsi, color=mode['rsi_up'])
    ax2.axhline(y=avg_rsi - std_rsi, color=mode['rsi_down'])
    ax2.axhline(y=avg_rsi, color=mode['rsi_avg'], linestyle='--')
    ax2.set_ylabel('RSI')
    leg = ax2.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    ax3.plot(so, color=mode['so'], label="Linia oscylatora")
    ax3.plot(so_signal, color=mode['so_signal'], label="Linia sygnału")
    ax3.axhline(y=avg_so + std_so, color=mode['so_up'])
    ax3.axhline(y=avg_so - std_so, color=mode['so_down'])
    ax3.axhline(y=avg_so, color=mode['so_avg'], linestyle="--")
    ax3.set_ylabel('Osc. stochastyczny')
    leg = ax3.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    plt.tight_layout()
    return save_plot_to_buffer()


def adx(data: pd.DataFrame, mode: dict, start: pd.Timestamp, adx_window: int) -> BytesIO:
    """
    Funkcja tworzy wykres ADX - wskaźnik trendu.
    :param data: DataFrame - dane do analizy z yfinance
    :param mode: dict - motyw wykresów
    :param start: Timestamp - data rozpoczęcia wykresu
    :param adx_window: int - okres ADX
    :return: BytesIO
    """
    c_adx = trend.adx(high=data['High'], low=data['Low'], close=data['Close'], window=adx_window)
    dipos = trend.adx_pos(high=data['High'], low=data['Low'], close=data['Close'], window=adx_window)
    dineg = trend.adx_neg(high=data['High'], low=data['Low'], close=data['Close'], window=adx_window)
    c_adx = c_adx.loc[start:]
    dipos = dipos.loc[start:]
    dineg = dineg.loc[start:]

    # chart
    fig, ax = plt.subplots(figsize=(10, 8))
    fig, axes = set_chart_style(fig, [ax], mode)
    ax = axes[0]

    c_adx.plot(ax=ax, label="ADX", color=mode['adx'])
    dipos.plot(ax=ax, label='+DI', color=mode['posdi'])
    dineg.plot(ax=ax, label='-DI', color=mode['negdi'])

    leg = ax.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    plt.tight_layout()
    return save_plot_to_buffer()


def macd(data: pd.DataFrame, mode: dict, start: pd.Timestamp, macd_slow: int, macd_fast: int,
         macd_sign: int) -> BytesIO:
    """
    Funkcja tworzy wykres MACD.
    :param data: DataFrame - dane do analizy z yfinance
    :param mode: dict - motyw wykresów
    :param start: Timestamp - data rozpoczęcia wykresu
    :param macd_slow: int - długi okres MACD
    :param macd_fast: int - krótki okres MACD
    :param macd_sign: int - okres sygnału MACD
    :return: BytesIO
    """
    macd_line = trend.macd(data['Close'], window_slow=macd_slow, window_fast=macd_fast)
    macd_signal = trend.macd_signal(data['Close'], window_slow=macd_slow, window_fast=macd_fast, window_sign=macd_sign)
    macd_diff = trend.macd_diff(data['Close'], window_slow=macd_slow, window_fast=macd_fast, window_sign=macd_sign)

    macd_line = macd_line.loc[start:]
    macd_signal = macd_signal.loc[start:]
    macd_diff = macd_diff.loc[start:]

    # chart
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig, axes = set_chart_style(fig, [ax1, ax2, ax3], mode)

    ax1, ax2, ax3 = axes

    ax1.plot(data['Close'].loc[macd_line.index[0]:macd_line.index[-1]], color=mode['price'], label='Cena')
    ax1.set_ylabel('Cena')
    leg = ax1.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    ax2.plot(macd_line, label='Linia MACD', color=mode['macd'])
    ax2.plot(macd_signal, label='Linia sygnału', color=mode['macd_signal'])
    ax2.set_ylabel("MACD")
    leg = ax2.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    bar_width = (macd_diff.index[1] - macd_diff.index[0]) * 0.7
    colors = [mode['mc_up'] if val >= 0 else mode['mc_down'] for val in macd_diff]
    ax3.bar(macd_diff.index, macd_diff, color=colors, width=bar_width)
    ax3.set_ylabel("Histogram MACD")

    plt.tight_layout()
    return save_plot_to_buffer()


def price_atr_ad(data: pd.DataFrame, mode: dict, start: pd.Timestamp, atr_ema_window: int, atr_window: int) -> BytesIO:
    """
    Funkcja tworzy wykres ceny z kanałami ATR.
    :param data: DataFrame - dane do analizy z yfinance
    :param mode: dict - motyw wykresów
    :param start: Timestamp - data rozpoczęcia wykresu
    :param atr_ema_window: int - okres średniej
    :param atr_window: int - okres ATR
    :return: BytesIO
    """
    ema = trend.ema_indicator(close=data['Close'], window=atr_ema_window).dropna()
    atr = volatility.average_true_range(high=data['High'], low=data['Low'], close=data['Close'], window=atr_window)
    a_d = volume.acc_dist_index(high=data['High'], low=data['Low'], close=data['Close'], volume=data['Volume'])

    ema = ema.loc[start:]
    atr = atr.loc[start:]
    data = data.loc[start:]
    a_d = a_d.loc[start:]

    # chart
    mc = mpf.make_marketcolors(up=mode['mc_up'], down=mode['mc_down'], edge=mode['mc_edge'], volume=mode['mc_volume'],
                               wick=mode['mc_wick'], ohlc=mode['mc_ohlc'])

    s = mpf.make_mpf_style(
        marketcolors=mc,
        facecolor=mode['face'],
        edgecolor=mode['edge'],
        figcolor=mode['fig'],
        gridcolor=mode['grid'],
        gridstyle='--',
        rc={'axes.labelcolor': mode['axes_label'], 'xtick.color': mode['xticks'],
            'ytick.color': mode['yticks']}
    )

    buffer = BytesIO()

    mpf.plot(data.loc[ema.index[0]:ema.index[-1]], type='ohlc', volume=True, style=s, show_nontrading=False,
             ylabel='Cena', ylabel_lower='Wolumen', figratio=(10, 8), figscale=1.5, tight_layout=True,
             ylim=(data['Low'].min() - atr.max(), data['High'].max() + atr.max()), savefig=buffer,
             addplot=[mpf.make_addplot(ema, color=mode['ema'], alpha=mode['alpha']),
                      mpf.make_addplot(ema + atr, color=mode['atr1'], alpha=mode['alpha'], linestyle='--'),
                      mpf.make_addplot(ema + 2 * atr, color=mode['atr2'], alpha=mode['alpha'], linestyle='dashdot'),
                      mpf.make_addplot(ema + 3 * atr, color=mode['atr3'], alpha=mode['alpha']),
                      mpf.make_addplot(ema - atr, color=mode['atr1'], alpha=mode['alpha'], linestyle='--'),
                      mpf.make_addplot(ema - 2 * atr, color=mode['atr2'], alpha=mode['alpha'], linestyle='dashdot'),
                      mpf.make_addplot(ema - 3 * atr, color=mode['atr3'], alpha=mode['alpha']),
                      mpf.make_addplot(a_d, panel='lower', color=mode['a_d'], secondary_y=True)])

    buffer.seek(0)
    plt.clf()
    plt.close()

    return buffer


def moving_averages(data: pd.DataFrame, mode: dict, start: pd.Timestamp, short_window: int, long_window: int) \
        -> BytesIO:
    """
    Funkcja tworzy wykres ADX - wskaźnik trendu.
    :param data: DataFrame - dane do analizy z yfinance
    :param mode: dict - motyw wykresów
    :param start: Timestamp - data rozpoczęcia wykresu
    :param short_window: int - okres krótkiej średniej
    :param long_window: int - okres długiej średniej
    :return: BytesIO
    """
    ema_short = trend.ema_indicator(data['Close'], window=short_window).dropna()
    ema_long = trend.ema_indicator(data['Close'], window=long_window).dropna()

    ema_short = ema_short.loc[start:]
    ema_long = ema_long.loc[start:]

    ema_diff = ema_short - ema_long

    # chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    fig, axes = set_chart_style(fig, [ax1, ax2], mode)

    ax1, ax2 = axes

    ax1.plot(data['Close'].loc[ema_long.index[0]:ema_long.index[-1]], color=mode['price'], label='Cena')
    ax1.plot(ema_short.loc[ema_long.index[0]:ema_long.index[-1]], color=mode['ema_short'], alpha=mode['alpha'],
             label='Krótsza średnia')
    ax1.plot(ema_long, color=mode['ema_long'], alpha=mode['alpha'], label='Dłuższa średnia')
    leg = ax1.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    bar_width = (ema_diff.index[1] - ema_diff.index[0]) * 0.7
    colors = [mode['mc_up'] if val >= 0 else mode['mc_down'] for val in ema_diff]
    ax2.bar(ema_diff.index, ema_diff, color=colors, width=bar_width)

    plt.tight_layout()

    return save_plot_to_buffer()
