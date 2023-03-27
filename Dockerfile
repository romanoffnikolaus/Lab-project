FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app

RUN mkdir /app/static & mkdir /app/media

RUN pip install -r requirements.txt