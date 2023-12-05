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
	wget https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-ubuntu-x86-64-avx2.tar && \
	tar -xvf stockfish-ubuntu-x86-64-avx2.tar && \
	rm stockfish-ubuntu-x86-64-avx2.tar



#add virtual environment to PATH
ENV PATH="/py/bin:$PATH"
ENV STOCKFISH_EXECUTABLE="/stockfish/stockfish-ubuntu-x86-64-avx2"
