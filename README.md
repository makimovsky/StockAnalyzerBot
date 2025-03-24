# ![StockAnalyzerBot](/docs/Stock_Analyzer_Bot.png)

StockAnalyzerBot is a Python-based bot that helps analyze financial markets.

## Getting Started
### Obtaining the Bot Token
To obtain a token, message [BotFather](https://t.me/BotFather) on Telegram and follow the instructions to create a bot.

### Running the Bot (Docker with Command-Line Argument)
You can start the bot using the following commands:
```
docker build -t your_tag --build-arg="BOT_TOKEN=your_bot_token" .
docker run your_tag
```

### Running the Bot (Docker with .env File)
Create a `.env` file in the project's root directory and add your bot token:
```
BOT_TOKEN=your_bot_token
```
Then, start the bot with:
```
docker build -t your_tag -f Dockerfile.dev .
docker run your_tag
```

## Using the Bot
### Available Commands:
```
/review (/r) [symbol] [period] [interval]

 Description:
   Displays data for the given symbol over the specified period with the chosen interval.

 Parameters:
   symbol: Stock symbol
   period: Data period
   interval: Data interval

 Example Usage:
   /r aapl 5y 1wk - Displays data for AAPL for the last 5 years with a 1-week time unit.


/rate [symbol]

 Description:
   Displays the rating of the company with the given symbol.

 Parameters:
   symbol: Stock symbol

 Example Usage:
   /rate aapl - Displays the rating for AAPL.


/ihelp (/ih) [atr/averages/rsi/os/adx/macd]

 Description:
   Provides guidance on interpreting charts and data sent by the bot.


/help (/h)

 Description:
   Displays the list of available commands.


/mode (/m) [light/dark/darkblue]

 Description:
   Changes the theme of displayed charts.
```

