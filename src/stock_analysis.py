import pandas as pd
import matplotlib.pyplot as plt
from ta import trend, momentum, volatility
from io import BytesIO
import mplfinance as mpf


def save_fig() -> BytesIO:
    plt.legend()
    plt.xlabel('')
    plt.ylabel('')
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    return buffer


def year_cycle_graph(data: pd.DataFrame, mode: dict, start: pd.Timestamp) -> BytesIO:
    fig, ax = plt.subplots(figsize=(10, 6))

    fig.patch.set_facecolor(mode['face'])
    ax.set_facecolor(mode['face'])

    p_start = pd.Timestamp(year=int(start.year), month=1, day=1)

    data = data.loc[p_start:]

    for year in data.index.year.unique():
        data_year = data[data.index.year == year]["Close"]
        data_year = data_year / data_year.max()
        data_year.index = data_year.index.strftime('%m-%d')
        data_year.plot(ax=ax, label=str(year))

    ax.spines['top'].set_color(mode['edge'])
    ax.spines['bottom'].set_color(mode['edge'])
    ax.spines['left'].set_color(mode['edge'])
    ax.spines['right'].set_color(mode['edge'])
    ax.tick_params(axis='x', colors=mode['tick_line'])
    ax.tick_params(axis='y', colors=mode['tick_line'])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(color=mode['face'])
    leg = ax.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    return buffer


def rsi_so_price(data: pd.DataFrame, mode: dict, start: pd.Timestamp) -> BytesIO:
    # RSI
    rsi = momentum.rsi(close=data["Close"], window=14).dropna()
    rsi = rsi.loc[start:]

    avg_rsi = rsi.mean()
    std_rsi = rsi.std()

    # Stochastics Oscilator
    so = momentum.stoch(high=data['High'], low=data['Low'], close=data['Close'], window=14, smooth_window=3).dropna()
    so_signal = momentum.stoch_signal(high=data['High'], low=data['Low'], close=data['Close'], window=14,
                                      smooth_window=3).dropna()
    so = so.loc[start:]
    so_signal = so_signal.loc[start:]

    avg_so = so.mean()
    std_so = so.std()

    # chart
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    fig.patch.set_facecolor(mode['face'])
    ax1.set_facecolor(mode['face'])
    ax2.set_facecolor(mode['face'])
    ax3.set_facecolor(mode['face'])

    ax1.plot(data['Close'].loc[rsi.index[0]:rsi.index[-1]], color=mode['price'], label='Cena')
    ax1.set_ylabel('Cena')
    ax1.spines['top'].set_color(mode['edge'])
    ax1.spines['bottom'].set_color(mode['edge'])
    ax1.spines['left'].set_color(mode['edge'])
    ax1.spines['right'].set_color(mode['edge'])
    ax1.tick_params(axis='x', colors=mode['axes_label'])
    ax1.tick_params(axis='y', colors=mode['axes_label'])
    ax1.yaxis.label.set_color(mode['axes_label'])
    ax1.xaxis.label.set_color(mode['axes_label'])
    ax1.title.set_color(mode['title'])
    ax1.grid(color=mode['grid'], linestyle='--')
    leg = ax1.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    ax2.plot(rsi, color=mode['rsi'], label="RSI")
    ax2.axhline(y=avg_rsi + std_rsi, color=mode['rsi_up'])
    ax2.axhline(y=avg_rsi - std_rsi, color=mode['rsi_down'])
    ax2.axhline(y=avg_rsi, color=mode['rsi_avg'], linestyle='--')
    ax2.set_ylabel('RSI')
    ax2.spines['top'].set_color(mode['edge'])
    ax2.spines['bottom'].set_color(mode['edge'])
    ax2.spines['left'].set_color(mode['edge'])
    ax2.spines['right'].set_color(mode['edge'])
    ax2.tick_params(axis='x', colors=mode['axes_label'])
    ax2.tick_params(axis='y', colors=mode['axes_label'])
    ax2.yaxis.label.set_color(mode['axes_label'])
    ax2.xaxis.label.set_color(mode['axes_label'])
    ax2.title.set_color(mode['title'])
    ax2.grid(color=mode['grid'], linestyle='--')
    leg = ax2.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    ax3.plot(so, color=mode['so'], label="Linia oscylatora")
    ax3.plot(so_signal, color=mode['so_signal'], label="Linia sygnału")
    ax3.axhline(y=avg_so + std_so, color=mode['so_up'])
    ax3.axhline(y=avg_so - std_so, color=mode['so_down'])
    ax3.axhline(y=avg_so, color=mode['so_avg'], linestyle="--")
    ax3.set_ylabel('Osc. stochastyczny')
    ax3.spines['top'].set_color(mode['edge'])
    ax3.spines['bottom'].set_color(mode['edge'])
    ax3.spines['left'].set_color(mode['edge'])
    ax3.spines['right'].set_color(mode['edge'])
    ax3.tick_params(axis='x', colors=mode['axes_label'])
    ax3.tick_params(axis='y', colors=mode['axes_label'])
    ax3.yaxis.label.set_color(mode['axes_label'])
    ax3.xaxis.label.set_color(mode['axes_label'])
    ax3.title.set_color(mode['title'])
    ax3.grid(color=mode['grid'], linestyle='--')
    leg = ax3.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    return buffer


def adx(data: pd.DataFrame, mode: dict, start: pd.Timestamp) -> BytesIO:
    c_adx = trend.adx(high=data['High'], low=data['Low'], close=data['Close'], window=14)
    dipos = trend.adx_pos(high=data['High'], low=data['Low'], close=data['Close'], window=14)
    dineg = trend.adx_neg(high=data['High'], low=data['Low'], close=data['Close'], window=14)
    c_adx = c_adx.loc[start:]
    dipos = dipos.loc[start:]
    dineg = dineg.loc[start:]

    # chart
    fig, ax = plt.subplots(figsize=(10, 6))

    fig.patch.set_facecolor(mode['face'])
    ax.set_facecolor(mode['face'])

    c_adx.plot(ax=ax, label="ADX", color=mode['adx'])
    dipos.plot(ax=ax, label='+DI', color=mode['posdi'])
    dineg.plot(ax=ax, label='-DI', color=mode['negdi'])

    ax.spines['top'].set_color(mode['edge'])
    ax.spines['bottom'].set_color(mode['edge'])
    ax.spines['left'].set_color(mode['edge'])
    ax.spines['right'].set_color(mode['edge'])
    ax.tick_params(axis='x', colors=mode['axes_label'])
    ax.tick_params(axis='y', colors=mode['axes_label'])
    ax.yaxis.label.set_color(mode['axes_label'])
    ax.xaxis.label.set_color(mode['axes_label'])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.title.set_color(mode['title'])
    ax.grid(color=mode['grid'], linestyle='--')
    leg = ax.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    return buffer


def macd(data: pd.DataFrame, mode: dict, start: pd.Timestamp) -> BytesIO:
    macd_line = trend.macd(data['Close'])
    macd_signal = trend.macd_signal(data['Close'])
    macd_diff = trend.macd_diff(data['Close'])

    macd_line = macd_line.loc[start:]
    macd_signal = macd_signal.loc[start:]
    macd_diff = macd_diff.loc[start:]

    # chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    fig.patch.set_facecolor(mode['face'])
    ax1.set_facecolor(mode['face'])
    ax2.set_facecolor(mode['face'])

    ax1.plot(macd_line, label='Linia MACD', color=mode['macd'])
    ax1.plot(macd_signal, label='Linia sygnału', color=mode['macd_signal'])
    ax1.set_ylabel("MACD")
    ax1.spines['top'].set_color(mode['edge'])
    ax1.spines['bottom'].set_color(mode['edge'])
    ax1.spines['left'].set_color(mode['edge'])
    ax1.spines['right'].set_color(mode['edge'])
    ax1.tick_params(axis='x', colors=mode['axes_label'])
    ax1.tick_params(axis='y', colors=mode['axes_label'])
    ax1.yaxis.label.set_color(mode['axes_label'])
    ax1.xaxis.label.set_color(mode['axes_label'])
    ax1.title.set_color(mode['title'])
    ax1.grid(color=mode['grid'], linestyle='--')
    leg = ax1.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    bar_width = (macd_diff.index[1] - macd_diff.index[0]) * 0.7
    colors = [mode['mc_up'] if val >= 0 else mode['mc_down'] for val in macd_diff]
    ax2.bar(macd_diff.index, macd_diff, color=colors, width=bar_width)
    ax2.set_ylabel("Różnica MACD-Linia sygnału")
    ax2.spines['top'].set_color(mode['edge'])
    ax2.spines['bottom'].set_color(mode['edge'])
    ax2.spines['left'].set_color(mode['edge'])
    ax2.spines['right'].set_color(mode['edge'])
    ax2.tick_params(axis='x', colors=mode['axes_label'])
    ax2.tick_params(axis='y', colors=mode['axes_label'])
    ax2.yaxis.label.set_color(mode['axes_label'])
    ax2.xaxis.label.set_color(mode['axes_label'])
    ax2.title.set_color(mode['title'])
    ax2.grid(color=mode['grid'], linestyle='--')

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    return buffer


def price_atr(data: pd.DataFrame, mode: dict, start: pd.Timestamp) -> BytesIO:
    ema = trend.ema_indicator(close=data['Close'], window=22).dropna()
    atr = volatility.average_true_range(high=data['High'], low=data['Low'], close=data['Close'], window=22)

    ema = ema.loc[start:]
    atr = atr.loc[start:]

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
                      mpf.make_addplot(ema - 3 * atr, color=mode['atr3'], alpha=mode['alpha'])])

    buffer.seek(0)
    plt.clf()

    return buffer


def moving_averages(data: pd.DataFrame, mode: dict, start: pd.Timestamp) -> BytesIO:
    ema_short = trend.ema_indicator(data['Close'], window=13).dropna()
    ema_long = trend.ema_indicator(data['Close'], window=26).dropna()

    ema_short = ema_short.loc[start:]
    ema_long = ema_long.loc[start:]

    ema_diff = ema_short - ema_long

    # chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    fig.patch.set_facecolor(mode['face'])
    ax1.set_facecolor(mode['face'])
    ax2.set_facecolor(mode['face'])

    ax1.plot(data['Close'].loc[ema_long.index[0]:ema_long.index[-1]], color=mode['price'], label='Cena')
    ax1.plot(ema_short.loc[ema_long.index[0]:ema_long.index[-1]], color=mode['ema_short'], alpha=mode['alpha'],
             label='Krótsza średnia')
    ax1.plot(ema_long, color=mode['ema_long'], alpha=mode['alpha'], label='Dłuższa średnia')
    ax1.spines['top'].set_color(mode['edge'])
    ax1.spines['bottom'].set_color(mode['edge'])
    ax1.spines['left'].set_color(mode['edge'])
    ax1.spines['right'].set_color(mode['edge'])
    ax1.tick_params(axis='x', colors=mode['axes_label'])
    ax1.tick_params(axis='y', colors=mode['axes_label'])
    ax1.yaxis.label.set_color(mode['axes_label'])
    ax1.xaxis.label.set_color(mode['axes_label'])
    ax1.title.set_color(mode['title'])
    ax1.grid(color=mode['grid'], linestyle='--')
    leg = ax1.legend()
    for text in leg.get_texts():
        text.set_color(mode['text'])

    bar_width = (ema_diff.index[1] - ema_diff.index[0]) * 0.7
    colors = [mode['mc_up'] if val >= 0 else mode['mc_down'] for val in ema_diff]
    ax2.bar(ema_diff.index, ema_diff, color=colors, width=bar_width)
    ax2.spines['top'].set_color(mode['edge'])
    ax2.spines['bottom'].set_color(mode['edge'])
    ax2.spines['left'].set_color(mode['edge'])
    ax2.spines['right'].set_color(mode['edge'])
    ax2.tick_params(axis='x', colors=mode['axes_label'])
    ax2.tick_params(axis='y', colors=mode['axes_label'])
    ax2.yaxis.label.set_color(mode['axes_label'])
    ax2.xaxis.label.set_color(mode['axes_label'])
    ax2.title.set_color(mode['title'])
    ax2.grid(color=mode['grid'], linestyle='--')

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    return buffer
