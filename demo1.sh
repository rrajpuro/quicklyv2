#!/bin/bash
echo "--------------------------- Running command: ip netns ---------------------------"
sudo ip netns
echo ""

echo "--------------------------- Running command: docker ps -a ---------------------------"
docker ps -a
echo ""

echo "--------------------------- Running command: ip netns exec org1 showipaddr ---------------------------"
sudo ip netns exec org1 ./scripts/showipaddr.py
echo ""

echo "--------------------------- Running command: ip netns exec org1 showipaddr ---------------------------"
sudo ip netns exec org2 ./scripts/showipaddr.py
echo ""

echo "--------------------------- Running command: ip netns exec org1 showipaddr ---------------------------"
sudo ip netns exec user1 ./scripts/showipaddr.py
echo ""

echo "--------------------------- Running command: etcdshow ---------------------------"
./scripts/etcdshow.sh
echo ""
