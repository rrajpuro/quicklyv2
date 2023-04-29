#!/bin/bash

docker ps -a --format '{{.Names}}' | grep -E '^[0-9]' | while read -r container_name ; do
  echo "Removing container $container_name"
  docker rm -f "$container_name"

done

# sudo ip netns | grep -E '^[0-9]' | awk '{print $1}' | xargs -I {} ip netns delete {}
sudo ip netns | grep -E '^[0-9]' | sed 's/ *(id: [0-9]*)$//g' | while read -r container_name ; do
  echo "Removing Namespace $container_name"
  sudo ip netns delete "$container_name"
done

etcdctl del '/' --prefix