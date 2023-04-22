#!/bin/bash
# etcdctl get "$1" --prefix | awk 'BEGIN { printf "%-25s%s\n", "Key", "Value" } { if (NR%2==1) { key=$0 } else { printf "%-25s%s\n", key, $0 } }'
# echo "Key            Value"
# etcdctl get "" --prefix | awk '{ if (NR%2==1) { key=$0; if (length(key)>max) { max=length(key) } } else { printf "%-*s %s\n", max, key, $0 } }' max=0 | column -t -s $'\t'
etcdctl get "" --prefix | awk 'BEGIN { printf "Key" "\t" "Value" "\n" "---" "\t" "-----" "\n" } { if (NR%2==1) { key=$0 } else { print key "\t" $0 } }' | column -t -s $'\t'