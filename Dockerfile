FROM python:3.8.1-slim

WORKDIR /app

COPY . .

RUN \
    pip install -r requirements.txt

ENV SPIDER_DB_LOGIN="andrey"
ENV SPIDER_DB_PWD="andrey"
ENV SPIDER_DB_HOST="192.168.1.36"
ENV SPIDER_DB_NAME="mydb"

ENTRYPOINT ["python", "/app/spider/spider.py"]
