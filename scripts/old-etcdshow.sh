#!/bin/bash
if [[ -z "$1" ]]; then
    prefix=""
else
    prefix="$1"
fi

$regex

etcdctl get --prefix "$prefix" | awk 'BEGIN { printf "Key" "\t" "Value" "\n" "---" "\t" "-----" "\n" } { if (NR%2==1) { key=$0 } else { print key "\t" $0 } }' | column -t -s $'\t | grep -E '$regex'
