# ![StockAnalyzerBot](/docs/Stock_Analyzer_Bot.png)

StockAnalyzerBot to Bot napisany w Pythonie, który pomaga analizować rynki finansowe.

## Uruchomienie
### Uzyskanie tokenu bota
Aby uzyskać token, należy napisać do [BotFather](https://t.me/BotFather) na Telegramie i postępować zgodnie z instrukcjami tworzenia Bota.

### Uruchomienie Bota (Docker z użyciem argumentu wywołania)
Bota można uruchomić komendami:
```
docker build -t twoj_tag --build-arg="BOT_TOKEN=token_twojego_bota" .
docker run twoj_tag
```

### Uruchomienie Bota (Docker z użyciem pliku .env)
W katalogu domowym projektu należy utworzyć plik .env i uzupełnić go tokenem:
```
BOT_TOKEN=token_twojego_bota
```
Następnie Bota można uruchomić komendami:
```
docker build -t twoj_tag -f Dockerfile.dev .
docker run twoj_tag
```

## Używanie Bota
### Dostępne komendy:
```
/review (/r) [symbol] [okres] [interwał]

 Opis:
   Komenda służy do wyświetlania danych
   o podanym symbolu w podanym
   okresie z podanym interwałem.

 Parametry:
   symbol: Symbol giełdowy
   okres: Okres danych
   interwał: Interwał danych

 Przykładowe użycie:
   /r aapl 5y 1wk - wyświetlenie danych o
   AAPL z ostatnich 5 lat z jednostką osi
   czasu 1 tydzień.


/rate [symbol]

 Opis:
   Komenda służy do wyświetlania oceny
   spółki o podanym symbolu.

 Parametry:
   symbol: Symbol giełdowy

 Przykładowe użycie:
   /rate aapl - wyświetlenie oceny AAPL.


/ihelp (/ih) [atr/średnie/rsi/os/adx/macd]

 Opis:
   Komenda służy do wyświetlenia
   pomocy dotyczącej interpretacji
   wysyłanych przez bota wykresów i
   danych.


/help (/h)

 Opis:
   Komenda służy do wyświetlenia
   dostępnych komend.


/mode (/m) [light/dark/darkblue]

 Opis:
   Komenda służy do zmiany motywu
   wyświetlanych wykresów.
```