FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
ENV POSTGRES_DSN=postgresql://postgres:postgres@postgres:5432/postgres

ENTRYPOINT [ "python3", "web_api.py" ]