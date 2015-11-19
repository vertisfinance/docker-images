#! /bin/bash

set -e

dir="$(dirname "$BASH_SOURCE")"

echo "vertisfinance/base"
echo "--------------------"
docker build -t vertisfinance/base "$dir/base/context"
