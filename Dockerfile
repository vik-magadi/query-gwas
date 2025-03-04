# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /usr/src/app

COPY . .

RUN pip3 install -r requirements.txt


CMD ["flask", "run", "--host=0.0.0.0"]

