#!/usr/bin/env bash
sleep_time=60
n_retries=5

for i in `seq 1 $n_retries`; do
    "$@" && exit 0
    sleep $sleep_time
done

exit 1
