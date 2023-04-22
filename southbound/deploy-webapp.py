import pexpect
import sys
import json

# print(sys.argv[1])
# with open('test.txt','w') as f:
#     f.write(sys.argv[1])
# exit(0)

# arg = json.loads(sys.argv[1])
# print(arg[0]['name'])
# exit(0)

arg = [
    {
        "instance": "ffff",
        "origin": {
            "vmid": 1166,
            "vmname": "vm11",
            "vmport": 3000,
            "vpcport": 80
        },
        "pop": [
            {
                "vmid": None,
                "vmname": None,
                "vmport": None,
                "vpcport": None
            },
            {
                "vmid": None,
                "vmname": None,
                "vmport": None,
                "vpcport": None
            },
            {
                "vmid": None,
                "vmname": None,
                "vmport": None,
                "vpcport": None
            }
        ]
    }
]

for cdn in arg:

    # Connect to the virtual machine console using virsh console
    child = pexpect.spawn(f'virsh console { cdn["origin"]["vmid"] } --force')
    child.logfile = sys.stdout.buffer

    # Wait for the login prompt and enter the username
    child.expect('Escape')
    child.sendline('')

    # Wait for the login prompt and enter the username
    r = child.expect(['login: ','\$'])
    if r == 0:
        child.sendline('vmadm')
        # Wait for the password prompt and enter the password
        child.expect('Password: ')
        child.sendline('vmadm')

    # Wait for the command prompt and enter the command to configure the IP address
    child.sendline('echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf')
    child.expect('\$')

    child.sendline('chmod +x ./webapp/webapp.sh')
    child.expect('\$')

    child.sendline(f'./webapp/webapp.sh { cdn["origin"]["vmport"] }')
    child.expect('WEBAPP Example app listening')

    # # Wait for the command to complete and exit the console
    # child.expect('\$')
    # child.sendline('exit')
    # # child.sendline('\u001d')
    # child.expect(pexpect.EOF)
    print(child.before.decode())
    print(str(child))
