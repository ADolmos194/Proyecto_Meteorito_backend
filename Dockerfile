FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /code_free

WORKDIR /code_free

COPY requirements.txt /code_free/

RUN python -m pip install -r requirements.txt

COPY . /code_free/
