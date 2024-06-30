from telegram import InlineKeyboardButton, InlineKeyboardMarkup

main_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Ustawienia", callback_data="settings")
    ],
])

settings_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='ATR', callback_data='atr')
    ],
    [
        InlineKeyboardButton(text='Średnie', callback_data='ma')
    ],
    [
        InlineKeyboardButton(text='RSI', callback_data='rsi')
    ],
    [
        InlineKeyboardButton(text='Osc. Stochastyczny', callback_data='so')
    ],
    [
        InlineKeyboardButton(text='Cykle roczne', callback_data='ycycles')
    ],
    [
        InlineKeyboardButton(text='ADX', callback_data='adx')
    ],
    [
        InlineKeyboardButton(text='MACD', callback_data='macd')
    ]
])

atr_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='')
    ]
])
