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

def configureContainer(logcon,tns):

    vpcip = '10.0.100.1/24'
    vpcint = f"v-log"

    logip = '10.0.100.2/24'
    logint = 'eth0'

    cmd = f'ip link add {logint} type veth peer name {vpcint}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd = f'ip link set {logint} netns {logcon}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd = f'ip link set {vpcint} netns {tns}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd = f'ip netns exec {tns} ip addr add {vpcip} dev {vpcint}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {tns} ip link set {vpcint} up'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {logcon} ip addr add {logip} dev {logint}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {logcon} ip link set {logint} up'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    cmd =  f'ip netns exec {logcon} ip route add default via {vpcip.split("/")[0]} dev {logint}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    # Removing default route created by docker towards docker0 bridge
    # subprocess.call( ip netns exec cs1 ip route del default ])
    
    return

def main(tenantkey):
    #Creating transit namespace
    tns = tenantkey+'transit'
    cmd =  f'ip netns add {tns}'
    print(f'Executing: {cmd}')
    subprocess.call(cmd, shell=True)
    
    logcon = tenantkey+'logserver'
    logport = '3090'
    vars = {
        'port': logport
    }
    created = deployContainer(logcon, image='nmadamshetti/logapp-node', env_vars=vars)
    if created:
        configureContainer(logcon, tns)

    return

if __name__=="__main__":
    print('Running from if __name__ block')
    main('07')
