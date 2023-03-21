# syntax=docker/dockerfile:1.0.0-experimental
FROM python:3.7.16-bullseye
WORKDIR /app

RUN /Scripts/activate.bat 
RUN python app.py