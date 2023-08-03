# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_REQUIRE_VIRTUALENV=false
RUN pip3 install certifi --upgrade
COPY flask-app flask-app
WORKDIR flask-app
RUN pip3 install virtualenv
RUN python3 -m venv onvif
RUN . onvif/bin/activate && pip install -r requirements.txt
RUN ls -a
RUN pwd
