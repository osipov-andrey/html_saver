FROM python:3.8.1-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "/app/spider/spider.py"]

CMD ["load", "https://yandex.ru", "--depth", "1"]
