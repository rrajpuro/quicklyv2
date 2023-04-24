import pexpect
import sys
import json
import re
import ipaddress as ip

subid = sys.argv[1]
gateway = sys.argv[2]

# Create a NAT rule for the subnet using first 3 octets of gateway ip
ipnet = ip.ip_network(gateway, strict=False)
natrule = f"-s { str(ipnet) } ! -d { str(ipnet) } -j MASQUERADE"
print('NAT rule: {natrule}')

# Connect to the virtual machine console using virsh console
child = pexpect.spawn(f'ip netns exec { subid[:4] } bash')
child.logfile = sys.stdout.buffer

# Check i the rule exists
child.expect('#')
r = child.sendline(f'iptables -t nat -C POSTROUTING { natrule }')

# Create the rule if doesn't exist
child.expect('#')
if re.search(r'(iptables: Bad rule)|(iptables: No chain)', child.before.decode()):
    child.sendline(f'iptables -t nat -A POSTROUTING { natrule }')
    child.expect('#')

child.sendline('exit')
# # child.sendline('\u001d')
child.expect(pexpect.EOF)
print(child.before.decode())
# print(str(child))
