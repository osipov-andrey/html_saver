FROM python:3.8.1-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/app/spider/spider.py"]

CMD ["db", "create"]
