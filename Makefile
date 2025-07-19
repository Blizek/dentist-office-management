include .env.local
export 

MAKE         := make --no-print-directory
APP_NAME     := $(APP_NAME_ENV)
APP_PORT     := $(APP_PORT_ENV)
APP_HOST	 := app
DOMAIN 		 := $(DOMAIN_ENV)
UID          := $(shell id -u)
GID          := $(shell id -g)
USER         := $(shell id -n -u)
ENV          := $(ENV_ENV)
DEBUG        := $(DEBUG_ENV)
DATE         := $(shell date +'%Y-%m-%d')
TIME         := $(shell date +'%H:%M:%S')
COMMIT       := $(shell git rev-parse HEAD)
COMMIT_MSG   := $(shell git log --format=%B -n 1 $(COMMIT))
AUTHOR       := $(firstword $(subst @, ,$(shell git show --format="%aE" $(COMMIT))))
BRANCH       := $(shell git rev-parse --abbrev-ref HEAD)
SQL_DATABASE := $(SQL_DATABASE)
SQL_USER     := $(SQL_USER_ENV)
SQL_PASSWORD := ${SQL_PASSWORD_ENV}
SQL_HOST     := $(SQL_HOST_ENV)
SQL_PORT     := $(SQL_PORT_ENV)
BUILD_DATE   := $(DATE) $(TIME)
CMPFILE      := docker-compose.yml
VERSION      := $(shell poetry version -s)
DOCO       	 := COMPOSE_PROJECT_NAME=${APP_NAME} RELEASE=$(VERSION) docker compose
MANAGE       := $(DOCO) exec -it app ./manage.py
#MANAGE      := ./manage.py

TOPDIR	     := $(shell pwd)
BINDIR	     := $(TOPDIR)/bin
PUBDIR	     := $(TOPDIR)/pub
LOGDIR	     := $(TOPDIR)/logs
ETCDIR	     := $(TOPDIR)/etc
RUNDIR	     := $(TOPDIR)/run

define ENV_BODY
ENV=${ENV}
DEBUG=${DEBUG}
SECRET_KEY=${SECRET_KEY_ENV}
DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE_ENV}
DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS_ENV}
DATABASE_URL=${DATABASE_URL_ENV}
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME_ENV}
SQL_ENGINE=${SQL_ENGINE_ENV}
DJANGO_SMSAPI_TOKEN=${DJANGO_SMSAPI_TOKEN_ENV}
POSTGRES_USER=${POSTGRES_USER_ENV}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_ENV}
POSTGRES_DB=${POSTGRES_DB_ENV}
SQL_HOST=${SQL_HOST_ENV}
SQL_PORT=${SQL_PORT_ENV}
endef

define CMPFILE_BODY
services:
  app:
    image: $(APP_NAME):$(VERSION)
    container_name: $(APP_NAME)-app
    hostname: app
    build:
      context: .
      dockerfile: Dockerfile
    user: $(APP_NAME)
    command: uvicorn $(APP_NAME).asgi:application --host 0.0.0.0 --port 8000 --reload --reload-include="*.html" --reload-include="*.css" --reload-include="*.js" --reload-include="*.json" --reload-include="*.toml" --reload-include="*.py"
    volumes:
     - .:/app
     - ./etc/pypoetry-config.toml:/home/$(APP_NAME)/.config/pypoetry/config.toml
    env_file:
      - .env
    depends_on:
      - db

  web:
    depends_on:
      - app
    image: nginx:1.27.2-alpine
    container_name: $(APP_NAME)-web
    hostname: web
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./etc/nginx/conf.d/:/etc/nginx/conf.d/
      - ./etc/nginx/cert/:/etc/nginx/cert/
      - ./etc/nginx/options-ssl-nginx.conf:/etc/nginx/options-ssl-nginx.conf
      - ./etc/nginx/ssl-dhparams.pem:/etc/nginx/ssl-dhparams.pem
      - ./pub/:/var/www/html/

  db:
    image: postgres:17
    container_name: $(APP_NAME)-db
    hostname: db
    volumes:
      - db_data:/var/lib/postgresql/data/
    env_file:
      - .env

volumes:
  db_data:
endef

define NGINX_CONF_BODY
# Virtual Host configuration for Dentman software
# HTTP - redirect to HTTPS
server {

    server_name ${DOMAIN};

    root ${PUBDIR};
    index index.html;
    error_log ${LOGDIR}/nginx-${DOMAIN}-error.log info;
    access_log ${LOGDIR}/nginx-${DOMAIN}-access.log;

    error_page 404 /error-404.html;
    error_page 502 /error-500.html;

    keepalive_timeout 300s;
    proxy_connect_timeout 300s;
    send_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;

    location / {
    	try_files $$uri @app;
    }

    location @app {
        proxy_set_header X-Forwarded-For $$proxy_add_x_forwarded_for;
        proxy_set_header Host $$http_host;
        proxy_redirect off;
        proxy_pass http://${APP_HOST}:${APP_PORT};
    }
    listen 443 ssl; # managed by Certbot
    ssl_certificate ${ETCDIR}/cert/${DOMAIN}/fullchain.pem; # managed by Certbot
    ssl_certificate_key ${ETCDIR}/cert/${DOMAIN}/privkey.pem; # managed by Certbot
    include ${ETCDIR}/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam ${ETCDIR}/ssl-dhparams.pem; # managed by Certbot

    client_max_body_size 10M;
}

server {
    if ($$host = ${DOMAIN}) {
        return 301 https://$$host$$request_uri;
    } # managed by Certbot


	listen 80;
	listen [::]:80;

	server_name ${DOMAIN};
    return 404; # managed by Certbot
}
endef

define SUPERVISOR_CONF_BODY
[program:${APP_NAME}-app-${ENV}]
directory = ${TOPDIR}
command = ${BINDIR}/app
user = ${APP_NAME}
group = ${APP_NAME}
stdout_logfile = ${LOGDIR}/supervisor-app-out.log
stderr_logfile = ${LOGDIR}/supervisor-app-err.log

[program:${APP_NAME}-worker-${ENV}]
directory = ${TOPDIR}
command = ${BINDIR}/worker
user = ${APP_NAME}
group = ${APP_NAME}
stdout_logfile = ${LOGDIR}/supervisor-worker-out.log
stderr_logfile = ${LOGDIR}/supervisor-worker-err.log
endef

define WORKER_BODY
#!/bin/bash
set -a
. ${TOPDIR}/.env
. ${TOPDIR}/.env.local
set +a
exec /usr/local/bin/celery -A ${APP_NAME}.celery worker --loglevel=info
endef

define APP_BODY
#!/bin/bash
set -a
. ${TOPDIR}/.env
. ${TOPDIR}/.env.local
set +a
exec uvicorn ${APP_NAME}.asgi:application --host 0.0.0.0 --port ${APP_PORT} --reload --reload-include="*.html" --reload-include="*.css" --reload-include="*.js" --reload-include="*.json" --reload-include="*.toml" --reload-include="*.py"
endef

define DEVAPP_BODY
#!/bin/bash
set -a
. ${TOPDIR}/.env
. ${TOPDIR}/.env.local
set +a
exec uvicorn ${APP_NAME}.asgi:application --reload  --host 127.0.0.1 --port ${APP_PORT} --reload-include="*.html"
endef

all: .env .env.local conf npm etc/nginx.conf

clean:
	rm -rf .env npm theme/tools/node_modules bin/app etc/supervisor.conf


npm: .env
	wget -O - https://nodejs.org/dist/v20.12.1/node-v20.12.1-linux-x64.tar.xz | tar -xJf -
	mv node-v20.12.1-linux-x64 npm
	cd theme/tools && npm install --global npm@latest
	cd theme/tools && npm install --global yarn
	cd theme/tools && npm install gulp@^4.0.2
	cd theme/tools && npm install --global gulp-cli
	cd theme/tools && yarn

theme-serve: npm
	cd theme/tools && gulp localhost

tag:
	git tag v${VERSION}

next: export CMPFILE_BODY:=$(CMPFILE_BODY)
next:
	poetry version patch
	make $(CMPFILE)
	make tag

$(CMPFILE): export CMPFILE_BODY:=$(CMPFILE_BODY)
$(CMPFILE): pyproject.toml
	echo "$${CMPFILE_BODY}" > $(CMPFILE)

env: export ENV_BODY:=$(ENV_BODY)
env:
	echo "$${ENV_BODY}" > .env
	pip3 install poetry
	poetry install

.env: export ENV_BODY:=$(ENV_BODY)
.env: .env.local
	echo "$${ENV_BODY}" > $@

.env.local:
	touch $@

create_compose: $(CMPFILE)

build: $(CMPFILE) .env
	$(DOCO) build --build-arg APP_GID=$(GID) --build-arg APP_UID=$(UID)  --build-arg APP_USER=$(APP_NAME)

build-no-cache: $(CMPFILE) .env
	$(DOCO) build --build-arg APP_GID=$(GID) --build-arg APP_UID=$(UID) --no-cache

up: .env
	$(DOCO) up

upd: .env
	$(DOCO) up -d

down: .env
	$(DOCO) down

psql: .env
	$(DOCO) run -it db psql

bash: .env
	$(DOCO) exec -it app bash

web: .env
	$(DOCO) exec -it --user root web sh

root: .env
	$(DOCO) exec -it --user root app bash

superuser: .env
	$(MANAGE) createsuperuser

shell: .env
	$(MANAGE) shell_plus

flush: .env
	$(MANAGE) flush

migrate: .env
	$(MANAGE) migrate

migrations: .env
	$(MANAGE) makemigrations

shell_plus: .env
	$(MANAGE) shell_plus

tests: .env
	pytest -p no:warnings

etc/nginx.conf: export NGINX_CONF_BODY:=$(NGINX_CONF_BODY)
etc/nginx.conf: .env
	echo "$${NGINX_CONF_BODY}" > $@

etc/supervisor.conf: export SUPERVISOR_CONF_BODY:=$(SUPERVISOR_CONF_BODY)
etc/supervisor.conf: .env
	echo "$${SUPERVISOR_CONF_BODY}" > $@

bin/worker: export WORKER_BODY:=$(WORKER_BODY)
bin/worker: .env
	echo "$${WORKER_BODY}" > $@
	chmod 755 $@

bin/app: export APP_BODY:=$(APP_BODY)
bin/app: .env
	echo "$${APP_BODY}" > $@
	chmod 755 $@

bin/devapp: export DEVAPP_BODY:=$(DEVAPP_BODY)
bin/devapp: .env
	echo "$${DEVAPP_BODY}" > $@
	chmod 755 $@

conf: etc/supervisor.conf bin/app bin/devapp bin/worker
	chmod 755 bin/*


sysinfo: .env
	@echo "DEBUG: '${DEBUG}'"
	@echo "APP_GID: '${APP_GID}'"
	@echo "APP_NAME: '${APP_NAME}'"
	@echo "APP_PORT: '${APP_PORT}'"
	@echo "APP_UID: '${APP_UID}'"
	@echo "DOMAIN: '${DOMAIN}'"
	@echo "PUBLIC_URL: '${PUBLIC_URL}'"
	@echo "MANAGE: '${MANAGE}'"
	@echo "TOPDIR: '${TOPDIR}'"
	@echo "BINDIR: '${BINDIR}'"
	@echo "ETCDIR: '${ETCDIR}'"
	@echo "LOGDIR: '${LOGDIR}'"
	@echo "PUBDIR: '${PUBDIR}'"
	@echo "RUNDIR: '${RUNDIR}'"
	@echo "USER: '${USER}'"
	@echo "UID: '${UID}'"
	@echo "GID: '${GID}'"
	@echo "BUILD_DATE: '${BUILD_DATE}'"
	@echo "VERSION: '${VERSION}'"
	@echo "BRANCH: '${BRANCH}'"
	@echo "ENV: '${ENV}'"
	@echo "BUILD_DATE: '${BUILD_DATE}'"
	@echo "AUTHOR: '${AUTHOR}'"
	@echo "COMMIT: '${COMMIT}'"
	@echo "COMMIT_MSG: '${COMMIT_MSG}'"
	@echo "VIRTUAL_ENV: '${VIRTUAL_ENV}'"
