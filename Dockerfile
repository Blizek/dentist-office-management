FROM ghcr.io/astral-sh/uv:latest AS uv_bin
FROM python:3.12-slim-bookworm

ARG APP_UID
ARG APP_GID
ARG APP_USER=dentman

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

COPY --from=uv_bin /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    libpq-dev \
    build-essential \
    libglib2.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN getent group ${APP_GID} || groupadd -g ${APP_GID} ${APP_USER} \
 && useradd -m -u ${APP_UID} -g ${APP_GID} -s /bin/bash ${APP_USER}

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

RUN chown -R ${APP_UID}:${APP_GID} /app

USER ${APP_USER}

RUN chmod +x /app/entry.sh
ENTRYPOINT ["/app/entry.sh"]