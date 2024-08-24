FROM python:3.12

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ='Europe/Oslo'
RUN apt-get update && apt-get install -y tzdata git cron && \
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

COPY src/ .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["sh", "/entrypoint.sh"]