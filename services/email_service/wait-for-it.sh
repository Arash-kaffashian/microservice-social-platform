#!/usr/bin/env bash
# Use: ./wait-for-it.sh host:port [-- command args]

set -e

TIMEOUT=15
QUIET=0

host_port=$1
shift || true

if [ -z "$host_port" ]; then
  echo "Usage: $0 host:port [-- command args]"
  exit 1
fi

host=$(echo $host_port | cut -d : -f 1)
port=$(echo $host_port | cut -d : -f 2)

# Wait until host:port is available
for i in $(seq $TIMEOUT); do
  nc -z "$host" "$port" >/dev/null 2>&1 && break
  echo "Waiting for $host:$port... ($i/$TIMEOUT)"
  sleep 1
done

# If command is provided, execute it
if [ $# -gt 0 ]; then
  exec "$@"
fi
