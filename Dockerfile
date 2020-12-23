FROM python:3.8.1-alpine

WORKDIR /app

#COPY ./requirements.txt ./

COPY . .

RUN \
    apk add --no-cache python3 postgresql-libs && \
    apk add --no-cache linux-headers && \
    apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
    pip install -r requirements.txt &&\
    source .env

CMD ["python", "/app/spider/spider.py"]

