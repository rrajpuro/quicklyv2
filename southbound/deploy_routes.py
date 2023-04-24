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

def configureLinks(vpcns, tns, tip, tipremote, vpcint, transint):

    cmd = f'ip link add {transint} type veth peer name {vpcint}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd = f'ip link set {transint} netns {tns}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd = f'ip link set {vpcint} netns {vpcns}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd = f'ip netns exec {tns} ip addr add {tipremote} dev {transint}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {tns} ip link set {transint} up'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {vpcns} ip addr add {tip} dev {vpcint}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {vpcns} ip link set {vpcint} up'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    # Removing default route created by docker towards docker0 bridge
    # subprocess.call( ip netns exec cs1 ip route del default ])
    
    return

def configureRoutes(vpcns, tipremote):
    nexthop = tipremote.split('/')[0]
    # ip netns exec {ns1} ip tunnel add {ns1if} mode gre remote {ns2_ip} local {ns1_ip} ttl 255
    # sudo ip netns exec 0701 ip route add 10.0.100.2 via 10.0.1.1
    # sudo ip netns exec 0701 iptables -t nat -A POSTROUTING -d 10.0.100.2/24 -j MASQUERADE
    cmd =  f'ip netns exec {vpcns} ip route add 10.0.100.2 via {nexthop}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {vpcns} iptables -t nat -A POSTROUTING -d 10.0.100.2/24 -j MASQUERADE'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    return

def main(vpckey, tenantkey, tip, tipremote):
    #Creating transit link
    tns = tenantkey+'transit'
    transint = f"v-{vpckey}"
    vpcint = "v-transit"
    configureLinks(vpckey, tns, tip, tipremote, vpcint, transint)
    configureRoutes(vpckey, tipremote)
    return

if __name__=="__main__":
    print('Running from if __name__ block')
    main('0701', '07', '10.0.1.2/24', '10.0.1.1/24')
