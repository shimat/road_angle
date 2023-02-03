FROM python:3.11-bullseye 

COPY requirements.txt /tmp/
RUN pip install -U pip \
  && pip install --no-cache-dir -r /tmp/requirements.txt
