#!/bin/bash
# Traceroute przy użyciu pinga
# Wiktor Stojek, 272383
# usage: ./tr_ping <host> <ttl_max> <size>
for i in $(seq 1 $2)
do
    ping -n -c 1 -t $i $1 -s $3
done;
