import docker
import subprocess
import os
import pexpect
import sys
import ipaddress

def deployContainer(conid, image='ubuntu', env_vars={}):
    print(f'Container deploying: {conid}')
    client = docker.from_env()
    # create container with the name 'sc1', interactive mode and without network
    try:
        container = client.containers.create(image, name=conid, tty=True, network_mode='none', environment=env_vars)
    except docker.errors.APIError as e:
        if '409 Client Error' in str(e) and 'Conflict' in str(e):
            print(f'Container name "{conid}" is already in use.')
            return False
        else:
            raise e
    # start the container
    container.start()
    # run the shell command
    subprocess.call(['./scripts/link-netns-container.sh', conid])
    print(f'Container deployed: {conid}')
    return True

def destroyContainer(conid):
    client = docker.from_env()
    # get the container by name
    try:
        container = client.containers.get(conid)
    except docker.errors.NotFound as e:
        print(f"Error: {e}")
        print(f'Container named "{conid}" does not exist.')
        return False
    # stop the container (if it is running)
    container.stop()
    # remove the container
    container.remove()
    # run the shell command
    subprocess.call(['sudo', 'ip', 'netns', 'del', conid])
    print(f'Container destroyed: {conid}')
    return True

def configureContainer(cdnname,vpckey,cdnip):
    ip_network = ipaddress.IPv4Network(cdnip, strict=False)
    mask = cdnip.split('/')[1]
    vpcip = str(ip_network.network_address)
    vpcint = f"v-{cdnname}"
    k = 'eth0'
    
    cmd = f'ip link add {k} type veth peer name {vpcint}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd = f'ip link set {k} netns {cdnname}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd = f'ip link set {vpcint} netns {vpckey}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd = f'ip netns exec {vpckey} ip addr add {vpcip+"/"+mask} dev {vpcint}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {vpckey} ip link set {vpcint} up'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {cdnname} ip addr add {cdnip} dev {k}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {cdnname} ip link set {k} up'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {cdnname} ip route add default via {vpcip} dev {k}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    # Removing default route created by docker towards docker0 bridge
    # subprocess.call( ip netns exec cs1 ip route del default ])
    
    return

def configureiptables(vpc, orgport, cdnipfull, cdnport):
    cdnip = cdnipfull.split('/')[0]
    cmd =  f'\
        ip netns exec {vpc} \
        iptables -t nat -A POSTROUTING -s {cdnipfull} ! -d {cdnipfull} -j MASQUERADE'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'\
        ip netns exec {vpc} \
        iptables --table nat --new-chain QUICKLY'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'\
        ip netns exec {vpc} \
        iptables -t nat -A PREROUTING -m addrtype --dst-type LOCAL \
        -p tcp -m tcp --dport {orgport} -j QUICKLY'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'\
        ip netns exec {vpc} \
        iptables -t nat -A QUICKLY -p tcp -m tcp --dport {orgport} -j DNAT --to-destination {cdnip}:{cdnport}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    return

def configureiptablesHA(vpc, orgport, cdnip1f, cdnip2f, cdnport):
    cdnip1 = cdnip1f.split('/')[0]
    cdnip2 = cdnip2f.split('/')[0]
    cmd =  f'\
        ip netns exec {vpc} \
        iptables -t nat -A POSTROUTING -s {cdnip1f} ! -d {cdnip1f} -j MASQUERADE'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'\
        ip netns exec {vpc} \
        iptables -t nat -A POSTROUTING -s {cdnip2f} ! -d {cdnip2f} -j MASQUERADE'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'\
        ip netns exec {vpc} \
        iptables --table nat --new-chain QUICKLY'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'\
        ip netns exec {vpc} \
        iptables -t nat -A PREROUTING -m addrtype --dst-type LOCAL -j QUICKLY'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'\
        ip netns exec {vpc} \
        iptables -t nat -A QUICKLY -p tcp -m tcp --dport {orgport} -m statistic --mode random --probability 0.5 -j DNAT --to-destination {cdnip1}:{cdnport}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'\
        ip netns exec {vpc} \
        iptables -t nat -A QUICKLY -p tcp -m tcp --dport {orgport} -j DNAT --to-destination {cdnip2}:{cdnport}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    return

def main(cdn,vpckey,log):
    cdnport = '3040'
    logport = '3090'
    logip = '10.0.100.1'
    vars = {
        'cdndomainname': cdn['cdndomainname'],
        'cdn_port': cdnport,
        'webapp_port': cdn['originport'],
        'webapp_IP': cdn['origin']
    }
    if log == 'True':
        vars = {
            'logapp_IP': logip,
            'logapp_port': logport,
            **vars
        }
    cdn1 = vpckey+'cdn1'
    created = deployContainer(cdn1, image='nmadamshetti/cdn-node', env_vars=vars)
    if created:
        configureContainer(cdn1,vpckey,cdn['primaryip'])

    if cdn['ha'] == 'True':
        cdn2 = vpckey+'cdn2'
        # Modyfying domain name for backup cache
        vars['cdndomainname'] = 'bak.'+vars['cdndomainname']
        created = deployContainer(cdn2, image='nmadamshetti/cdn-node', env_vars=vars)
        if created:
            configureContainer(cdn2,vpckey,cdn['secondaryip'])
        configureiptablesHA(vpckey, cdn['originport'], cdn['primaryip'], cdn['secondaryip'], cdnport)
    else:
        configureiptables(vpckey, cdn['originport'], cdn['primaryip'], cdnport)

    return

if __name__=="__main__":
    print('Running from if __name__ block')
    # cdn = {
    #     'origin': '1.1.1.1',
    #     'originport':'3060',
    #     'ha': 'True',
    #     'primaryip': '192.168.150.1/31',
    #     'secondaryip': '192.168.150.3/31'
    # }
    # main(cdn, '007', 'True')
