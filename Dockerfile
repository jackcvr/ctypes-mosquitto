FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y libmosquitto1 time git

RUN pip install -U \
    pip \
    py-spy \
    pytest \
    pytest-asyncio \
    build \
    twine \
    matplotlib \
    paho-mqtt \
    aiomqtt \
    amqtt \
    gmqtt \
    mqttools

ADD . ./

RUN pip install -e .
