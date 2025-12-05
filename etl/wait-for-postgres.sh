#!/bin/bash
# PostgreSQL'in hazır olmasını bekleyen script

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  >&2 echo "PostgreSQL henüz hazır değil - bekleniyor..."
  sleep 1
done

>&2 echo "PostgreSQL hazır - komut çalıştırılıyor"
exec $cmd

