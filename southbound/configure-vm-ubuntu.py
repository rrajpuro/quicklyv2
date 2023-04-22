import pexpect
import sys

vmid = (sys.argv[1])

# Connect to the virtual machine console using virsh console
child = pexpect.spawn(f'virsh console { vmid }')
child.logfile = sys.stdout.buffer

# Wait for the login prompt and enter the username
child.expect('Escape')
child.sendline('')

# Wait for the login prompt and enter the username
while True:
    r = child.expect(['login:','\$'])
    if r == 0:
        child.sendline('vmadm')
        # Wait for the password prompt and enter the password
        child.expect('Password:')
        child.sendline('vmadm')
        s = child.expect(['Login incorrect', '\$'])
        if s == 0:
            continue
        elif s == 1:
            break
    elif r == 1:
        break

# Wait for the command prompt
child.sendline('')
child.expect('\$')

# Write netconf file into /etc/netplan
# file = /var/quickly/tenant/{id}/vpc-{vpcid}/vm-{vmid}/vm-{vmid}-netconf
with open(f'/var/quickly/tenant/{vmid[:2]}/vpc-{vmid[:4]}/vm-{vmid}/vm-{vmid}-netconf') as f:
    n = f.read()
# sudo bash -c 'echo -e "dfsd\ndfgdfg\nsdfgdf\n" > /etc/netplan/t.yaml'
child.sendline(f"sudo bash -c 'echo -e \"{n}\" > /etc/netplan/test.yaml'")
child.expect('\$')

child.sendline('sudo netplan apply')
child.expect('\$')
child.sendline('')
child.expect('\$')

# Wait for the command to complete and exit the console
child.sendline('\u001d')
child.expect(pexpect.EOF)
print(child.before.decode())
