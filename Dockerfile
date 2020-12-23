FROM python:3.8.1-alpine

WORKDIR /app

COPY . .

RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache libxml2-dev libxslt-dev && \
    apk add --no-cache linux-headers && \
    apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
    pip install -r requirements.txt

ENV SPIDER_DB_LOGIN="andrey"
ENV SPIDER_DB_PWD="andrey"
ENV SPIDER_DB_HOST="192.168.1.36"
ENV SPIDER_DB_NAME="mydb"

ENTRYPOINT ["python", "/app/spider/spider.py"]
