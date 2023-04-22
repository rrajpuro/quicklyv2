#!/bin/bash
CONTAINER_NAME=$1
CONTAINER_PID=$(docker inspect --format '{{.State.Pid}}' $CONTAINER_NAME)
ln -sf /proc/$CONTAINER_PID/ns/net /var/run/netns/$CONTAINER_NAME
