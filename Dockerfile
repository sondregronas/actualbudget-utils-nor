FROM python:3.12

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ='Europe/Oslo'

RUN apt-get update -qq -y && \
    apt-get install -y \
        tzdata git \
        libasound2 \
        libatk-bridge2.0-0 \
        libgtk-4-1 \
        libnss3 \
        xdg-utils \
        wget && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV ACTUAL_URL="http://127.0.0.1:5006"
ENV ACTUAL_PWD=""
ENV ACTUAL_ENCRYPTION_PASSWORD=""
ENV ACTUAL_FILE="My Budget"
ENV ACTUAL_PAYEE=""
ENV ACTUAL_CAR_ACCOUNT="Bil"
ENV ACTUAL_MORTGAGE_ACCOUNT="Bolig"

ENV LICENSE_PLATES=""
ENV HJEMLA_URLS=""

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chrome
RUN wget -q -O chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.70/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip && \
    rm chrome-linux64.zip && \
    mv chrome-linux64 /opt/chrome/ && \
    ln -s /opt/chrome/chrome /usr/local/bin/ && \
    wget -q -O chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.70/linux64/chromedriver-linux64.zip && \
    unzip -j chromedriver-linux64.zip chromedriver-linux64/chromedriver && \
    rm chromedriver-linux64.zip && \
    mv chromedriver /usr/local/bin/

COPY src/ .

ENTRYPOINT ["python", "/app/routine.py"]
