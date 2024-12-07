#!/bin/bash

HOST=$1
shift
CMD="$@"

echo "Host: $HOST"
echo "Command: $CMD"
echo "Waiting 10 seconds before checking RabbitMQ..."
sleep 10

while ! nc -z $HOST; do
  echo "Waiting for $HOST to be ready..."
  sleep 2
done

echo "$HOST is ready!"
echo "Running command: $CMD"
exec $CMD
