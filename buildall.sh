#! /bin/bash

set -e

dir="$(dirname "$BASH_SOURCE")"

for name in base postgres
do
    echo "vertisfinance/$name"
    echo "-------------------"
    docker build -t "vertisfinance/$name" "$dir/$name/context"
done
