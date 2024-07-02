from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import yaml

main_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Ustawienia", callback_data="settings")
    ],
])

settings_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='ATR >', callback_data='atr')
    ],
    [
        InlineKeyboardButton(text='Średnie >', callback_data='ma')
    ],
    [
        InlineKeyboardButton(text='RSI >', callback_data='rsi')
    ],
    [
        InlineKeyboardButton(text='Osc. Stochastyczny >', callback_data='so')
    ],
    [
        InlineKeyboardButton(text='ADX >', callback_data='adx')
    ],
    [
        InlineKeyboardButton(text='MACD >', callback_data='macd')
    ],
    [
        InlineKeyboardButton(text='Motyw >', callback_data='cb_mode')
    ]
])

atr_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='Zmień okres średniej >', callback_data='atr_ema_window')
    ],
    [
        InlineKeyboardButton(text='Zmień okres ATR >', callback_data='atr_window')
    ],
    [
        InlineKeyboardButton(text='< Powrót', callback_data='set_return')
    ]
])

ma_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='Zmień okres krótkiej średniej >', callback_data='ema_short')
    ],
    [
        InlineKeyboardButton(text='Zmień okres długiej średniej >', callback_data='ema_long')
    ],
    [
        InlineKeyboardButton(text='< Powrót', callback_data='set_return')
    ]
])

rsi_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='Zmień okres RSI >', callback_data='rsi_window')
    ],
    [
        InlineKeyboardButton(text='< Powrót', callback_data='set_return')
    ]
])

so_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='Zmień okres osc. stochastycznego >', callback_data='so_window')
    ],
    [
        InlineKeyboardButton(text='Zmień okres sygnału >', callback_data='so_smooth_window')
    ],
    [
        InlineKeyboardButton(text='< Powrót', callback_data='set_return')
    ]
])

adx_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='Zmień okres ADX >', callback_data='adx_window')
    ],
    [
        InlineKeyboardButton(text='< Powrót', callback_data='set_return')
    ]
])

macd_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='Zmień krótki okres MACD >', callback_data='macd_fast')
    ],
    [
        InlineKeyboardButton(text='Zmień długi okres MACD >', callback_data='macd_slow')
    ],
    [
        InlineKeyboardButton(text='Zmień okres sygnału MACD >', callback_data='macd_sign')
    ],
    [
        InlineKeyboardButton(text='< Powrót', callback_data='set_return')
    ]
])

with open('modes.yml', 'r') as file:
    modes = yaml.safe_load(file)

modes_keyboard = [[InlineKeyboardButton(text=mode, callback_data=mode)] for mode in list(modes.keys())]
modes_keyboard.append([InlineKeyboardButton(text='< Powrót', callback_data='set_return')])
modes_markup = InlineKeyboardMarkup(modes_keyboard)
