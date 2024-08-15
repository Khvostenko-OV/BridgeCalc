FROM python:3.8.5
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

ARG ENVIRONMENT
RUN pip install -r /app/requirements.txt

COPY . /app
