# Use an official Python runtime as a parent image
FROM python:3.11-alpine3.18

#set environment variables
ENV PYTHONUNBUFFERED 1

#set work directory
COPY ./requirements.txt /requirements.txt
COPY ./app /app
WORKDIR /app

EXPOSE 8000

RUN python -m venv /py && \
	/py/bin/pip install --upgrade pip && \
	/py/bin/pip install -r /requirements.txt

#add virtual environment to PATH
ENV PATH="/py/bin:$PATH"