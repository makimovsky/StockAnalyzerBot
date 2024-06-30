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
        InlineKeyboardButton(text='Cykle roczne >', callback_data='ycycles')
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
        InlineKeyboardButton(text='Okres średniej >', callback_data='atr_ema_window')
    ],
    [
        InlineKeyboardButton(text='Okres ATR >', callback_data='atr_atr_window')
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
