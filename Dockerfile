# JUNOSPACE - xLink Relay Bot
# Copyright (c) Juno

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "xlink.py"]
