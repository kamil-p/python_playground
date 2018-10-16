FROM python:3.7-slim

RUN apt-get update \
    && apt-get clean \
    && apt-get autoclean \
    && apt-get --purge autoremove
    && rm /etc/localtime \
    && ln -s /usr/share/zoneinfo/Europe/Warsaw /etc/localtime \
    && "date" \
    && pip install --no-cache-dir pipenv

WORKDIR /usr/src/app

COPY ./Pipfile ./Pipfile.lock

RUN pipenv install --system