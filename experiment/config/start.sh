#! /bin/bash

function signal_handler {
    exit
}

trap signal_handler SIGTERM SIGINT

i=0
while [ ${i} -lt 10 ]; do
    echo ${i}
    i=$[${i}+1]
    sleep 3
done
