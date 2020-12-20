FROM python:3.8.1-alpine

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]

