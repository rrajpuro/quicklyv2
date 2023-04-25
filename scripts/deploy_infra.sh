#!/bin/bash
docker create -it --name org1 --network none -e port=3060 nmadamshetti/webapp-node
docker start org1
sudo ./scripts/link-netns-container.sh org1
sudo ip link add eth0 type veth peer name v-org1
sudo ip addr add 1.1.1.2/24 dev v-org1
sudo ip link set v-org1 up
sudo ip link set eth0 netns org1
sudo ip netns exec org1 ip addr add 1.1.1.1/24 dev eth0
sudo ip netns exec org1 ip link set eth0 up
sudo ip netns exec org1 ip route add default via 1.1.1.2 dev eth0

# sudo ip netns del org1
# docker rm -f org1 

#!/bin/bash
docker create -it --name user1 --network none rrajpur/ubuntu-quickly
docker start user1
sudo ./scripts/link-netns-container.sh user1
sudo ip link add eth0 type veth peer name v-user1
sudo ip addr add 5.5.5.2/24 dev v-user1
sudo ip link set v-user1 up
sudo ip link set eth0 netns user1
sudo ip netns exec user1 ip addr add 5.5.5.1/24 dev eth0
sudo ip netns exec user1 ip link set eth0 up
sudo ip netns exec user1 ip route add default via 5.5.5.2 dev eth0


#!/bin/bash
docker create -it --name org2 --network none -e port=3060 nmadamshetti/webapp-node
docker start org2
sudo ./scripts/link-netns-container.sh org2
sudo ip link add eth0 type veth peer name v-org2
sudo ip addr add 2.2.2.1/24 dev v-org2
sudo ip link set v-org2 up
sudo ip link set eth0 netns org2
sudo ip netns exec org2 ip addr add 2.2.2.2/24 dev eth0
sudo ip netns exec org2 ip link set eth0 up
sudo ip netns exec org2 ip route add default via 2.2.2.1 dev eth0