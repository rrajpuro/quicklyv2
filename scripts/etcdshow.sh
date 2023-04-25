#!/bin/bash
# Parse command line options
while [[ $# -gt 0 ]]
do
    key="$1"

    case $key in
        -p|--prefix)
        prefix="$2"
        shift
        shift
        ;;
        -r|--regex)
        regex="$2"
        shift
        shift
        ;;
        *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Set default values for prefix and regex if not provided
if [[ -z "$prefix" ]]; then
    prefix=""
fi

if [[ -z "$regex" ]]; then
    regex=".*"
fi

# Get keys from etcd and filter based on prefix and regex
etcdctl get --prefix "$prefix" | awk 'BEGIN { printf "Key" "\t" "Value" "\n" "---" "\t" "-----" "\n" } { if (NR%2==1) { key=$0 } else { print key "\t" $0 } }' | column -t -s $'\t' | grep -E "$regex"
