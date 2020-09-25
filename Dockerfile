FROM python:3.6-alpine
MAINTAINER Sebastián Zapata "szapata@dcc.uchile.cl"

RUN pip3 install pyTelegramBotAPI python-dotenv

ENV TZ=America/Santiago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY PuntitoFwBot.py /
COPY FwBot.db /
