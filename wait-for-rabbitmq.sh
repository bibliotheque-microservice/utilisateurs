#!/bin/bash

HOST=$1
shift
CMD="$@"

echo "Waiting 10 seconds before checking RabbitMQ..."
sleep 10  # Délai avant de commencer la vérification

# Attente active avec while
while ! nc -z $HOST; do
  echo "Waiting for $HOST to be ready..."
  sleep 2
done

echo "$HOST is ready!"
exec $CMD
