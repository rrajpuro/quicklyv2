import yaml
from ansible_runner import run
from filelock import Timeout, FileLock
from southbound import deploy_container
import os
from pprint import pprint as pp

# print(f"Controller: {os.getcwd()}")
# print(deploy_container.main())
# exit(0)

states = ['requested', 'processing', 'active', 'terminate']

database = "test_master_db.yaml"
# lock_path = f"{database}.lock"
# lock = FileLock(lock_path, timeout=1)

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
    with open(database, 'w') as f:
        yaml.dump(data, f, sort_keys=False)
    return

def check_requests(data):
    for tenantkey,tenantval in data['tenants'].items():
        if tenantval['state'] == states[0]:
            data['tenants'][tenantkey]['state'] = states[1]
            update_db(data)
            print(f'Tenant requested: {tenantval["name"]}')
            create_tenant(tenantkey)
            print(f'Tenant created: {tenantval["name"]}')
            data['tenants'][tenantkey]['state'] = states[2]
            update_db(data)
            
        for vpckey, vpcval in (tenantval['vpcs']).items():
            if vpcval['state'] == states[0]:
                data['tenants'][tenantkey]['vpcs'][vpckey]['state'] = states[1]
                update_db(data)
                print(f'VPC requested: {vpcval["name"]}')
                create_vpc(vpckey, vpcval)
                print(f'VPC created: {vpcval["name"]}')
                data['tenants'][tenantkey]['vpcs'][vpckey]['state'] = states[2]
                update_db(data)

            if 'subnets' in vpcval.keys():
                for subkey,subval in (vpcval['subnets']).items():
                    if subval['state'] == states[0]:
                        data['tenants'][tenantkey]['vpcs'][vpckey]['subnets'][subkey]['state'] = states[1]
                        update_db(data)
                        print(f'Subnet requested: {subval["name"]}')
                        create_subnet(subkey, subval)
                        print(f'Subnet created: {subval["name"]}')
                        data['tenants'][tenantkey]['vpcs'][vpckey]['subnets'][subkey]['state'] = states[2]
                        update_db(data)
            
            if 'vms' in vpcval.keys():
                for vmk, vmv in (vpcval['vms']).items():
                    if vmv['state'] == states[0]:
                        data['tenants'][tenantkey]['vpcs'][vpckey]['vms'][vmk]['state'] = states[1]
                        update_db(data)
                        print(f'VM requested: {vmv["name"]}')
                        create_vm(vmk, vmv)
                        print(f'VM created: {vmv["name"]}')
                        data['tenants'][tenantkey]['vpcs'][vpckey]['vms'][vmk]['state'] = states[2]
                        update_db(data)

            if 'containers' in vpcval.keys():
                for conkey, conval in (vpcval['containers']).items():
                    if conval['state'] == states[0]:
                        data['tenants'][tenantkey]['vpcs'][vpckey]['containers'][conkey]['state'] = states[1]
                        update_db(data)
                        print(f'Container requested: {conval["name"]}')
                        create_container(conkey, conval)
                        print(f'Container created: {conval["name"]}')
                        data['tenants'][tenantkey]['vpcs'][vpckey]['containers'][conkey]['state'] = states[2]
                        update_db(data)

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

if __name__ == '__main__':
    
    with open(database, 'r') as f:
        data = yaml.safe_load(f)
    
    check_requests(data)
    
    # lock.release()