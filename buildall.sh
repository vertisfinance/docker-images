#! /bin/bash

set -e

dir="$(dirname "$BASH_SOURCE")"

for name in base postgres django-py3 nginx
do
    out="vertisfinance/${name}"
    outlen=${#out}
    line=$(head -c ${outlen} < /dev/zero | tr '\0' '-')
    echo $(tput setaf 3)${out}$(tput sgr0)
    echo $(tput setaf 2)${line}$(tput sgr0)
    docker build -t "vertisfinance/$name" "$dir/$name/context"
done
