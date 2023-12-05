# Use an official Python runtime as a parent image
FROM python:3.11-bullseye

#set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

#set work directory
COPY ./requirements.txt /django/requirements.txt
WORKDIR /django

#the server will listen on port 8000
EXPOSE 8000

SHELL ["/bin/bash", "-c"]

RUN python -m venv /py && \
	source /py/bin/activate && \
	/py/bin/pip install --upgrade pip && \
	/py/bin/pip install -r requirements.txt && \
	cd / && \
	git clone https://github.com/official-stockfish/Stockfish.git && \
	cd Stockfish/src && \
	make -j build

#add virtual environment to PATH
ENV PATH="/py/bin:$PATH"
ENV STOCKFISH_EXECUTABLE="/Stockfish/src/stockfish"
