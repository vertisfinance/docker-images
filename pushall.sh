#! /bin/bash

set -e

for i in */
do
    name=$(basename "$i")
    echo pushing vertisfinance/${name}
    echo -----------------------------
    docker push vertisfinance/${name}
done
