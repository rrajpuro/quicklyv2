import docker
import subprocess
import os
import pexpect
import sys

def deployContainer(conid):
    print(f'Container deploying: {conid}')
    client = docker.from_env()
    # create container with the name 'sc1', interactive mode and without network
    try:
        container = client.containers.create('ubuntu', name=conid, tty=True, network_mode='none')
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

def configureContainer(conid, data):
    vpc = conid[:4]
    infs = data['interfaces']
    for k,v in infs.items():
        bridge = v['subid']
        ipaddr = v['ipaddr']
        gateway = v['gateway']
        vpcint = f"{conid}-{k}"
        cmd = f'ip link add {k} type veth peer name {vpcint}'
        print(f'Executing: {cmd}')
        subprocess.call(cmd, shell=True)
        cmd = f'ip link set {k} netns {conid}'
        print(f'Executing: {cmd}')
        subprocess.call(cmd, shell=True)
        cmd = f'ip link set {vpcint} netns {vpc}'
        print(f'Executing: {cmd}')
        subprocess.call(cmd, shell=True)
        cmd = f'ip netns exec {vpc} brctl addif {bridge} {vpcint}'
        print(f'Executing: {cmd}')
        subprocess.call(cmd, shell=True)
        cmd =  f'ip netns exec {vpc} ip link set {vpcint} up'
        print(f'Executing: {cmd}')
        subprocess.call(cmd, shell=True)
        cmd =  f'ip netns exec {conid} ip addr add {ipaddr} dev {k}'
        print(f'Executing: {cmd}')
        subprocess.call(cmd, shell=True)
        cmd =  f'ip netns exec {conid} ip link set {k} up'
        print(f'Executing: {cmd}')
        subprocess.call(cmd, shell=True)
        cmd =  f'ip netns exec {conid} ip route add default via {gateway} dev {k}'
        print(f'Executing: {cmd}')
        subprocess.call(cmd, shell=True)
        # Removing default route created by docker towards docker0 bridge
        # subprocess.call( ip netns exec cs1 ip route del default ])
    
    return

def main(conid,data):
    created = deployContainer(conid)
    if created:
        configureContainer(conid, data)
    return

if __name__=="__main__":
    print('Running from if __name__ block')
