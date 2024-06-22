import pandas as pd
import matplotlib.pyplot as plt
from ta import trend, momentum, volatility
from io import BytesIO
import mplfinance as mpf


def save_fig(title="") -> BytesIO:
    plt.title(title)
    plt.legend()
    plt.xlabel('')
    plt.ylabel('')
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    return buffer


def year_cycle_graph(data: pd.DataFrame) -> BytesIO:
    for year in data.index.year.unique():
        data_year = data[data.index.year == year]["Close"]
        data_year = data_year / data_year.max()
        data_year.index = data_year.index.strftime('%m-%d')
        data_year.plot(label=year)
    plt.xticks([])
    plt.yticks([])
    chart = save_fig("Wykres cykli rocznych")

    return chart


def rsi_so_price(data: pd.DataFrame) -> tuple:
    # RSI
    rsi = momentum.rsi(close=data["Close"], window=14)
    rsi.dropna(inplace=True)

    avg_rsi = rsi.mean()
    std_rsi = rsi.std()
    act_rsi = rsi.iloc[-1]

    # Stochastics Oscilator
    so = momentum.stoch(high=data['High'], low=data['Low'], close=data['Close'], window=14, smooth_window=3)
    so_signal = momentum.stoch_signal(high=data['High'], low=data['Low'], close=data['Close'], window=14, smooth_window=3)
    so.dropna(inplace=True)

    avg_so = so.mean()
    std_so = so.std()
    act_so = so.iloc[-1]

    # chart
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    ax1.plot(data['Close'], color="red")
    ax1.set_ylabel('Cena')

    ax2.plot(rsi, color="orange", label="RSI")
    ax2.axhline(y=avg_rsi + std_rsi, color="orange")
    ax2.axhline(y=avg_rsi - std_rsi, color="orange")
    ax2.axhline(y=avg_rsi, color="orange", linestyle="--")
    ax2.set_ylabel('RSI')
    ax2.legend()

    ax3.plot(so, color="blue", label="Linia oscylatora")
    ax3.plot(so_signal, color="pink", label="Linia sygnału")
    ax3.axhline(y=avg_so + std_so, color="blue")
    ax3.axhline(y=avg_so - std_so, color="blue")
    ax3.axhline(y=avg_so, color="blue", linestyle="--")
    ax3.set_ylabel('Osc. stochastyczny')
    ax3.legend()

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    return round(avg_rsi, 2), round(std_rsi, 2), round(act_rsi, 2), round(avg_so, 2), round(std_so, 2), \
        round(act_so, 2), buffer


def adx(data: pd.DataFrame) -> BytesIO:
    c_adx = trend.adx(high=data['High'], low=data['Low'], close=data['Close'], window=14)
    c_adx = c_adx[c_adx != 0.0]

    # chart
    c_adx.plot(label="ADX", color="black")
    plt.axhline(y=20, color="green", label="Linia przebicia")
    plt.axhline(y=40, color="red", linestyle="--", label="Linia uwagi")

    chart = save_fig("Wskaźnik trendu - ADX")

    return chart


def macd(data: pd.DataFrame) -> BytesIO:
    macd_line = trend.macd(data['Close'])
    macd_signal = trend.macd_signal(data['Close'])
    macd_diff = trend.macd_diff(data['Close'])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(macd_line, label='Linia MACD', color='blue')
    ax1.plot(macd_signal, label='Linia sygnału', color='red')
    ax1.set_ylabel("MACD")
    ax1.legend()

    colors = ['green' if val >= 0 else 'red' for val in macd_diff]
    ax2.bar(macd_diff.index, macd_diff, color=colors, width=0.5)
    ax2.set_ylabel("Różnica MACD-Linia sygnału")

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    return buffer


def price_bollinger(data: pd.DataFrame) -> BytesIO:
    bollinger = volatility.BollingerBands(close=data['Close'], window=20, window_dev=2)
    b_avg = bollinger.bollinger_mavg()
    b_hb = bollinger.bollinger_hband()
    b_lb = bollinger.bollinger_lband()

    # Plot candlestick chart with Bollinger Bands
    mc = mpf.make_marketcolors(up='g', down='r', edge='inherit', volume='inherit')
    s = mpf.make_mpf_style(marketcolors=mc)

    buffer = BytesIO()

    mpf.plot(data, type='candle', volume=True, style=s, show_nontrading=False, savefig=buffer,
             title="Wykres świecowy ze wstęgami Bollingera", ylabel='Cena', ylabel_lower='Wolumen', figratio=(10, 8),
             figscale=1.5, tight_layout=True, addplot=[mpf.make_addplot(b_avg, color='blue', alpha=0.5),
                                                       mpf.make_addplot(b_hb, color='orange', alpha=0.6),
                                                       mpf.make_addplot(b_lb, color='orange', alpha=0.6)])

    buffer.seek(0)
    plt.clf()

    return buffer

