#!/bin/bash
docker create -it --name org1 --network none -e port=3060 nmadamshetti/webapp-node
docker start org1