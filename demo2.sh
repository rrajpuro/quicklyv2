#!/bin/bash
# echo "--------------------------- Running command: ip netns ---------------------------"
# sudo ip netns
# echo ""
sudo -E python3 runner.py

python3 northboundv2.py customer_input_template_blue.yaml

python3 northboundv2.py customer_input_template_red.yaml

sudo -E python3 northboundv2.py

sudo -E python3 northboundv2.py customer_input_template_blue.yaml

sudo -E python3 northboundv2.py customer_input_template_red.yaml