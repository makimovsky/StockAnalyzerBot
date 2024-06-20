import datetime

import pandas as pd
import matplotlib.pyplot as plt


def save_fig(filename, title=""):
    plt.title(title)
    plt.legend()
    plt.xticks([])
    plt.yticks([])
    plt.xlabel('')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(f'../resources/{filename}')
    plt.clf()


def year_cycle_graph(data: pd.DataFrame) -> None:
    for year in data.index.year.unique():
        data_year = data[data.index.year == year]["Close"]
        data_year = data_year / data_year.max()
        data_year.index = data_year.index.strftime('%m-%d')
        data_year.plot(label=year)
    save_fig('ycycle.png', "Wykres cykli rocznych")


def rsi_so_price(data: pd.DataFrame) -> tuple:
    # RSI
    period = 14
    delta = data['Close'].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    avg_rsi = rsi.mean()
    std_rsi = rsi.std()
    act_rsi = rsi.iloc[-1]

    # Stochastics Oscilator
    highest_high = data['High'].rolling(window=period).max()
    lowest_low = data['Low'].rolling(window=period).min()

    so = ((data['Close'] - lowest_low) / (highest_high - lowest_low)) * 100

    avg_so = so.mean()
    std_so = so.std()
    act_so = so.iloc[-1]

    # chart
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=365)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    ax1.plot(data['Close'], color="red")
    ax1.set_xlim(start, end)
    ax1.set_ylabel('Cena')

    ax2.plot(rsi, color="orange")
    ax2.set_xlim(start, end)
    ax2.axhline(y=avg_rsi + std_rsi, color="orange")
    ax2.axhline(y=avg_rsi - std_rsi, color="orange")
    ax2.axhline(y=avg_rsi, color="orange", linestyle="--")
    ax2.set_ylabel('RSI')

    ax3.plot(so, color="blue")
    ax3.set_xlim(start, end)
    ax3.axhline(y=avg_so + std_so, color="blue")
    ax3.axhline(y=avg_so - std_so, color="blue")
    ax3.axhline(y=avg_so, color="blue", linestyle="--")
    ax3.set_ylabel('Osc. stochastyczny')

    plt.tight_layout()
    plt.savefig("../resources/rop.png")
    plt.clf()

    return round(avg_rsi, 2), round(std_rsi, 2), round(act_rsi, 2), round(avg_so, 2), round(std_so, 2), \
        round(act_so, 2)
