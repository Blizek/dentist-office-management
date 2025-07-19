# pull official base image
FROM python:3.12-slim-bookworm
ARG APP_UID
ARG APP_GID
ARG APP_USER
# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd libpq-dev build-essential libglib2.0-0 libpangocairo-1.0-0
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN /usr/local/bin/pip install poetry
RUN groupadd ${APP_USER}
RUN useradd -m -s /bin/bash -g ${APP_USER} ${APP_USER}

COPY . .
RUN /bin/true\
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction \
    && rm -rf /root/.cache/pypoetry
# RUN poetry install
USER ${APP_USER}
COPY ./entry.sh .

ENTRYPOINT ["/app/entry.sh"]