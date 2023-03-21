FROM python:3.7.16-bullseye
WORKDIR /app

RUN Scripts/activate.bat & python app.py