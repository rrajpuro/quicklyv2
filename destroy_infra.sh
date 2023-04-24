#!/bin/bash
docker rm -f 08logserver 
docker rm -f 0802cdn1 
docker rm -f 080211

sudo ip netns del 0801
sudo ip netns del 08logserver
sudo ip netns del 08transit
sudo ip netns del 0802
sudo ip netns del 080211
sudo ip netns del 080111
sudo ip netns del 0802cdn1
sudo ip netns del 0802cdn1
sudo ip netns del 080211
sudo ip netns del 0802
sudo ip netns del 0801
sudo ip netns del 08logserver
sudo ip netns del 08transit

docker ps -a
ip netns



sudo ip netns del 0802cdn1
sudo ip netns del 080211
sudo ip netns del 0802
sudo ip netns del 0801cdn2
sudo ip netns del 0801cdn1
sudo ip netns del 0801
sudo ip netns del 08logserver
sudo ip netns del 08transit

docker rm -f 0802cdn1
docker rm -f 080211
docker rm -f 0802
docker rm -f 0801cdn2
docker rm -f 0801cdn1
docker rm -f 0801
docker rm -f 08logserver
docker rm -f 08transit
