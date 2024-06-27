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


def year_cycle_graph(data: pd.DataFrame, mode: dict) -> BytesIO:
    fig, ax = plt.subplots(figsize=(10, 6))

    fig.patch.set_facecolor(mode['face'])
    ax.set_facecolor(mode['face'])

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


def rsi_so_price(data: pd.DataFrame, mode: dict) -> tuple:
    # RSI
    rsi = momentum.rsi(close=data["Close"], window=14).dropna()

    avg_rsi = rsi.mean()
    std_rsi = rsi.std()
    act_rsi = rsi.iloc[-1]

    # Stochastics Oscilator
    so = momentum.stoch(high=data['High'], low=data['Low'], close=data['Close'], window=14, smooth_window=3).dropna()
    so_signal = momentum.stoch_signal(high=data['High'], low=data['Low'], close=data['Close'], window=14,
                                      smooth_window=3).dropna()

    avg_so = so.mean()
    std_so = so.std()
    act_so = so.iloc[-1]

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

    return round(avg_rsi, 2), round(std_rsi, 2), round(act_rsi, 2), round(avg_so, 2), round(std_so, 2), \
        round(act_so, 2), buffer


def adx(data: pd.DataFrame, mode: dict) -> BytesIO:
    c_adx = trend.adx(high=data['High'], low=data['Low'], close=data['Close'], window=14)
    c_adx = c_adx[c_adx != 0.0]

    # chart
    fig, ax = plt.subplots(figsize=(10, 6))

    fig.patch.set_facecolor(mode['face'])
    ax.set_facecolor(mode['face'])

    c_adx.plot(ax=ax, label="ADX", color=mode['adx'])

    plt.axhline(y=20, color=mode['adx20'], label="Linia przebicia")
    plt.axhline(y=40, color=mode['adx40'], linestyle='--', label="Linia uwagi")

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

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    return buffer


def macd(data: pd.DataFrame, mode: dict) -> BytesIO:
    macd_line = trend.macd(data['Close'])
    macd_signal = trend.macd_signal(data['Close'])
    macd_diff = trend.macd_diff(data['Close'])

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


def price_bollinger(data: pd.DataFrame, mode: dict) -> BytesIO:
    bollinger = volatility.BollingerBands(close=data['Close'], window=20, window_dev=2)
    b_avg = bollinger.bollinger_mavg().dropna()
    b_hb = bollinger.bollinger_hband().dropna()
    b_lb = bollinger.bollinger_lband().dropna()

    mc = mpf.make_marketcolors(up=mode['mc_up'], down=mode['mc_down'], edge=mode['mc_edge'], volume=mode['mc_volume'],
                               wick=mode['mc_wick'])

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

    mpf.plot(data.loc[b_avg.index[0]:b_avg.index[-1]], type='candle', volume=True, style=s, show_nontrading=False,
             savefig=buffer, ylabel='Cena', ylabel_lower='Wolumen', figratio=(10, 8), figscale=1.5, tight_layout=True,
             addplot=[mpf.make_addplot(b_avg, color=mode['bollinger'], alpha=0.5),
                      mpf.make_addplot(b_hb, color=mode['bollinger_up'], alpha=0.6),
                      mpf.make_addplot(b_lb, color=mode['bollinger_down'], alpha=0.6)])

    buffer.seek(0)
    plt.clf()

    return buffer


def moving_averages(data: pd.DataFrame, mode: dict) -> BytesIO:
    sma10 = trend.sma_indicator(data['Close'], window=10).dropna()
    sma50 = trend.sma_indicator(data['Close'], window=50).dropna()
    sma_diff = sma10 - sma50

    # chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    fig.patch.set_facecolor(mode['face'])
    ax1.set_facecolor(mode['face'])
    ax2.set_facecolor(mode['face'])

    ax1.plot(data['Close'].loc[sma50.index[0]:sma50.index[-1]], color=mode['price'], label='Cena')
    ax1.plot(sma10.loc[sma50.index[0]:sma50.index[-1]], color=mode['sma10'], alpha=0.7, label='10-okresów')
    ax1.plot(sma50, color=mode['sma50'], alpha=0.7, label='50-okresów')
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

    bar_width = (sma_diff.index[1] - sma_diff.index[0]) * 0.7
    colors = [mode['mc_up'] if val >= 0 else mode['mc_down'] for val in sma_diff]
    ax2.bar(sma_diff.index, sma_diff, color=colors, width=bar_width)
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
