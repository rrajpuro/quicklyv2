#!/bin/bash
docker rm -f 08logserver 
docker rm -f 0802cdn1 
docker rm -f 080211

sudo ip netns del 0801
sudo ip netns del 08logserver
sudo ip netns del 08transit
sudo ip netns del 0802
sudo ip netns del 080211
sudo ip netns del 0802cdn1
sudo ip netns del 0802cdn1
sudo ip netns del 080211
sudo ip netns del 0802
sudo ip netns del 0801
sudo ip netns del 08logserver
sudo ip netns del 08transit

docker ps -a
ip netns