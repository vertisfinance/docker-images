#! /bin/bash

set -e

dir="$(dirname "$BASH_SOURCE")"
basename=vertisfinance

for name in base postgres django-py3 nginx nodejs
do
    out="${basename}/${name}"
    outlen=${#out}
    line=$(head -c ${outlen} < /dev/zero | tr '\0' '-')
    echo $(tput setaf 3)${out}$(tput sgr0)
    echo $(tput setaf 2)${line}$(tput sgr0)
    docker build -t ${out} ${dir}/${name}/context
done
