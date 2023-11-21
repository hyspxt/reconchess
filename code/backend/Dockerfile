# Use an official Python runtime as a parent image
FROM python:3.11-alpine3.18

#set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

#set work directory
COPY ./requirements.txt /django/requirements.txt
WORKDIR /django

#the server will listen on port 8000
EXPOSE 8000

RUN apk update && \
    apk add --no-cache build-base sdl2-dev && \
	apk add --no-cache build-base freetype-dev && \
	apk add --no-cache build-base libffi-dev && \
	python -m venv /py && \
	source /py/bin/activate && \
	/py/bin/pip install --upgrade pip && \
	/py/bin/pip install -r requirements.txt


#add virtual environment to PATH
ENV PATH="/py/bin:$PATH"