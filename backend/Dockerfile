FROM python:latest
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./movies_admin/requirements/dev.txt /code/
COPY ./movies_admin/requirements/base.txt /code/
COPY ./db.sqlite /code/
RUN pip install -r dev.txt
COPY . /code/

