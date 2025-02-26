FROM python:3.12.4-alpine3.19

COPY ./requirements.txt /requirements.txt
RUN python -m  venv /venv && /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt && rm requirements.txt

COPY ./src /app
ARG BOT_TOKEN

ENV BOT_TOKEN=${BOT_TOKEN}

WORKDIR /app

ENV PATH="/venv/bin:$PATH"

CMD ["python3", "bot.py"]