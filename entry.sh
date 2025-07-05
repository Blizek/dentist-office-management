#!/bin/bash

echo "Waiting for PostgreSQL DB..."

while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done

echo "PostgreSQL DB started"

exec $@
