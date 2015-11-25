#! /bin/bash

set -e

for i in */
do
    name=$(basename ${i})
    out="pushing vertisfinance/${name}"
    outlen=${#out}
    line=$(head -c ${outlen} < /dev/zero | tr '\0' '-')
    echo $(tput setaf 3)${out}$(tput sgr0)
    echo $(tput setaf 2)${line}$(tput sgr0)
    docker push vertisfinance/${name}
done
