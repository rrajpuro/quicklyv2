import os
import yaml
from ansible_runner import run
from filelock import Timeout, FileLock
from southbound import deploy_container, deploy_cdn, deploy_logserver, deploy_routes
from pprint import pprint as pp

states = ['requested', 'processing', 'active', 'terminate']

def convert_to_dict(args):
    result = {}
    for value, meta in args:
        key = meta.key.decode("utf-8")  # convert byte string to regular string
        key_list = key.split("/")
        current_dict = result
        for k in key_list[1:-1]:
            if k not in current_dict:
                current_dict[k] = {}
            current_dict = current_dict[k]
        current_dict[key_list[-1]] = value.decode("utf-8")
    return result

def convert_to_kv_pairs(d, prefix="/"):
    result = []
    for k, v in d.items():
        if isinstance(v, dict):
            result.extend(convert_to_kv_pairs(v, prefix=f"{prefix}{k}/"))
        else:
            # if isinstance(v,bool):
            result.append((f"{prefix}{k}", v))
    return result

def run_playbook(filename, vars:dict):

    # Define the custom variables
    # vars = {'web_server': 'example.com', 'port': '8080'}

    # Define the Ansible Runner configuration
    config = {
        'private_data_dir': './',
        'playbook': filename,
        'extravars': vars
    }

    # Run the Ansible playbook using Ansible Runner
    result = run(**config)

    # Print the output
    # print(result.stdout.read())
    return result

def update_db(data):
    with open(data, 'w') as f:
        yaml.dump(data, f, sort_keys=False)
    return

def check_requests(data, etcd):
    for tenantkey,tenantval in data['tenants'].items():
        if tenantval['state'] == states[0]:
            etcd.put(f'/tenants/{tenantkey}/state', states[1])
            print(f'Tenant requested: {tenantval["name"]}')
            create_tenant(tenantkey)
            #create a logging server and a transit vpc
            if 'logging' in tenantval.keys() and tenantval['logging'] == 'True':
                create_logserver(tenantkey)
            print(f'Tenant created: {tenantval["name"]}')
            etcd.put(f'/tenants/{tenantkey}/state', states[2])
            
        for vpckey, vpcval in (tenantval['vpcs']).items():
            if vpcval['state'] == states[0]:
                etcd.put(f'/tenants/{tenantkey}/vpcs/{vpckey}/state', states[1])
                print(f'VPC requested: {vpcval["name"]}')
                create_vpc(vpckey, vpcval)
                #connect vpc with transit if requested
                if 'logging' in tenantval.keys() and tenantval['logging'] == 'True':
                    deploy_routes.main(vpckey, tenantkey, vpcval['tip'], vpcval['tipremote'])
                print(f'VPC created: {vpcval["name"]}')
                etcd.put(f'/tenants/{tenantkey}/vpcs/{vpckey}/state', states[2])

            if 'subnets' in vpcval.keys():
                for subkey,subval in (vpcval['subnets']).items():
                    if subval['state'] == states[0]:
                        etcd.put(f'/tenants/{tenantkey}/vpcs/{vpckey}/subnets/{subkey}/state', states[1])
                        print(f'Subnet requested: {subval["name"]}')
                        create_subnet(subkey, subval)
                        print(f'Subnet created: {subval["name"]}')
                        etcd.put(f'/tenants/{tenantkey}/vpcs/{vpckey}/subnets/{subkey}/state', states[2])
            
            if 'vms' in vpcval.keys():
                for vmk, vmv in (vpcval['vms']).items():
                    if vmv['state'] == states[0]:
                        etcd.put(f'/tenants/{tenantkey}/vpcs/{vpckey}/vms/{vmk}/state', states[1])
                        print(f'VM requested: {vmv["name"]}')
                        create_vm(vmk, vmv)
                        print(f'VM created: {vmv["name"]}')
                        etcd.put(f'/tenants/{tenantkey}/vpcs/{vpckey}/vms/{vmk}/state', states[2])

            if 'containers' in vpcval.keys():
                for conkey, conval in (vpcval['containers']).items():
                    if conval['state'] == states[0]:
                        etcd.put(f'/tenants/{tenantkey}/vpcs/{vpckey}/containers/{conkey}/state', states[1])
                        print(f'Container requested: {conval["name"]}')
                        create_container(conkey, conval)
                        print(f'Container created: {conval["name"]}')
                        etcd.put(f'/tenants/{tenantkey}/vpcs/{vpckey}/containers/{conkey}/state', states[2])

            if 'cdn' in vpcval.keys():
                cdn = vpcval['cdn']
                if cdn['state'] == states[0]:
                    etcd.put(f'/tenants/{tenantkey}/vpcs/{vpckey}/cdn/state', states[1])
                    print(f'CDN requested with origin: {cdn["origin"]}:{cdn["originport"]}')
                    if 'logging' in tenantval.keys() and tenantval['logging'] == 'True':
                        # create cdnwith logging
                        create_cdn(cdn, vpckey, 'True')
                    else:
                        #create cdn without logging
                        create_cdn(cdn, vpckey, None)
                    print(f'CDN deployed with local: {cdn["primaryip"]}')
                    etcd.put(f'/tenants/{tenantkey}/vpcs/{vpckey}/cdn/state', states[2])

    return

def create_tenant(tenant):
    run_playbook('southbound/onboard-tenant.yaml', {'id':tenant})
    return

def create_vpc(vpcid, vpc):
    run_playbook('southbound/create-namespace.yaml', {'vpcid':vpcid, **vpc})
    return

def create_subnet(subid, subnet):
    run_playbook('southbound/create-subnet.yaml', {'subid':subid, **subnet})
    return

def create_vm(vmid, vm):
    run_playbook('southbound/create-vm.yaml', vm.update({'vmid':vmid}))
    return

def create_container(conname,con):
    deploy_container.main(conname,con)
    return

def create_cdn(cdn, vpckey, logip):
    deploy_cdn.main(cdn, vpckey, logip)
    return

def create_logserver(tenantkey):
    deploy_logserver.main(tenantkey)
    return

def maincon(etcd_client):
    
    db = convert_to_dict(etcd_client.get_all())
    check_requests(db, etcd_client)

    return

if __name__ == '__main__':
    pass