FROM python:3.12-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ='Europe/Oslo'

RUN apt-get update -qq -y && \
    apt-get install -y tzdata && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ .

ENTRYPOINT ["python", "/app/routine.py"]
