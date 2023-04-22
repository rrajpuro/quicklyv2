import yaml
from ansible_runner import run
from filelock import Timeout, FileLock

states = ['requested', 'processing', 'active', 'terminate']

database = "hw4q2.yaml"
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
    for i,ten in enumerate(data['tenants']):
        if ten['state'] == states[0]:
            data['tenants'][i]['state'] = states[1]
            update_db(data)
            print(f'Tenant requested: {ten["name"]}')
            create_tenant(ten)
            print(f'Tenant created: {ten["name"]}')
            data['tenants'][i]['state'] = states[2]
            update_db(data)
            
        for j,vpc in enumerate(ten['vpcs']):
            if vpc['state'] == states[0]:
                data['tenants'][i]['vpcs'][j]['state'] = states[1]
                update_db(data)
                print(f'VPC requested: {vpc["name"]}')
                create_vpc(vpc)
                print(f'VPC created: {vpc["name"]}')
                data['tenants'][i]['vpcs'][j]['state'] = states[2]
                update_db(data)

            for k,subnet in enumerate(vpc['subnets']):
                if subnet['state'] == states[0]:
                    data['tenants'][i]['vpcs'][j]['subnets'][k]['state'] = states[1]
                    update_db(data)
                    print(f'Subnet requested: {subnet["name"]}')
                    create_subnet(subnet)
                    print(f'Subnet created: {subnet["name"]}')
                    data['tenants'][i]['vpcs'][j]['subnets'][k]['state'] = states[2]
                    update_db(data)

            for k,vm in enumerate(vpc['vms']):
                if vm['state'] == states[0]:
                    data['tenants'][i]['vpcs'][j]['vms'][k]['state'] = states[1]
                    update_db(data)
                    print(f'VM requested: {vm["name"]}')
                    create_vm(vm)
                    print(f'VM created: {vm["name"]}')
                    data['tenants'][i]['vpcs'][j]['vms'][k]['state'] = states[2]
                    update_db(data)

    return

def create_tenant(tenant):
    run_playbook('southbound/onboard-tenant.yaml', tenant)
    return

def create_vpc(vpc):
    run_playbook('southbound/create-namespace.yaml', vpc)
    return

def create_subnet(subnet):
    run_playbook('southbound/create-subnet.yaml', subnet)
    return

def create_vm(vm):
    run_playbook('southbound/create-vm.yaml', vm)
    return

if __name__ == '__main__':

    # vars = {
    #     'vms' : [
    #         {
    #             "capacity": 12,
    #             "image_path": "/var/quickly/base/jammy-server-cloudimg-amd64-disk-kvm.img",
    #             "interface": [
    #                 {
    #                     "ipaddr": "192.168.131.2/24",
    #                     "mac": "52:54:00:12:34:56",
    #                     "name": "enp0s2",
    #                     "subid": "1144"
    #                 }
    #             ],
    #             "memory": 2048,
    #             "name": "vm11",
    #             "state": "requested/provisioning/running/stopped",
    #             "vcpu": 2,
    #             "vmid": "1155"
    #         }
    #     ]
    # }
    # run_playbook('test.yaml', vars)
    # exit(0)
    # lock.acquire()
    
    with open(database, 'r') as f:
        data = yaml.safe_load(f)
    
    check_requests(data)
    
    # lock.release()