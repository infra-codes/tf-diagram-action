FROM python:3.13-slim

RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/app/main.py"]
