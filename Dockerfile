# syntax=docker/dockerfile:1.0.0-experimental
FROM python:3.7.16-bullseye
WORKDIR /app

RUN pip install flask
RUN pip install flask-limiter
RUN pip install Flask-restful
RUN python app.py