import pandas as pd
import matplotlib.pyplot as plt
from ta import trend, momentum


def save_fig(filename, title=""):
    plt.title(title)
    plt.legend()
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
    plt.xticks([])
    plt.yticks([])
    save_fig('ycycle.png', "Wykres cykli rocznych")


def rsi_so_price(data: pd.DataFrame) -> tuple:
    # RSI
    rsi = momentum.rsi(close=data["Close"], window=14)
    rsi.dropna(inplace=True)

    avg_rsi = rsi.mean()
    std_rsi = rsi.std()
    act_rsi = rsi.iloc[-1]

    # Stochastics Oscilator
    so = momentum.stoch(high=data['High'], low=data['Low'], close=data['Close'], window=14, smooth_window=3)
    so.dropna(inplace=True)

    avg_so = so.mean()
    std_so = so.std()
    act_so = so.iloc[-1]

    # chart
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    ax1.plot(data['Close'], color="red")
    ax1.set_ylabel('Cena')

    ax2.plot(rsi, color="orange")
    ax2.axhline(y=avg_rsi + std_rsi, color="orange")
    ax2.axhline(y=avg_rsi - std_rsi, color="orange")
    ax2.axhline(y=avg_rsi, color="orange", linestyle="--")
    ax2.set_ylabel('RSI')

    ax3.plot(so, color="blue")
    ax3.axhline(y=avg_so + std_so, color="blue")
    ax3.axhline(y=avg_so - std_so, color="blue")
    ax3.axhline(y=avg_so, color="blue", linestyle="--")
    ax3.set_ylabel('Osc. stochastyczny')

    plt.tight_layout()
    plt.savefig("../resources/rop.png")
    plt.clf()

    return round(avg_rsi, 2), round(std_rsi, 2), round(act_rsi, 2), round(avg_so, 2), round(std_so, 2), \
        round(act_so, 2)


def adx(data: pd.DataFrame) -> None:
    c_adx = trend.adx(high=data['High'], low=data['Low'], close=data['Close'], window=14)
    c_adx = c_adx[c_adx != 0.0]

    # chart
    c_adx.plot(label="ADX", color="black")
    plt.axhline(y=20, color="green", label="Linia przebicia")
    plt.axhline(y=40, color="red", linestyle="--", label="Linia uwagi")

    save_fig("adx.png", "Wskaźnik trendu - ADX")
