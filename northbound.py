import yaml
import random 

with open('sample_input.yaml', 'r') as f:
    data = yaml.safe_load(f)

org_name = data['name']
vpcs = []

new_tenant = {
    'id': str(random.randint(0, 99)),
    'name': org_name,
    'state': 'requested'

}

for vpc in data['vpcs']:
    vpc_data = {
        'vpcid': new_tenant['id'] + str(random.randint(0, 99)),
        'name': vpc['name'],
        'location': vpc['location'],
        'state': 'requested',
        'pip': '',
        'cip': '',
        'subnets': [],
    }
    for subnet in vpc['subnets']:
        subnet_data = {
            'subid': vpc_data['vpcid'] + str(random.randint(0, 99)),
            'name': subnet['name'],
            'mode': subnet['mode'],
            'gateway': subnet['gateway'],
            'dhcp': subnet.get('dhcp', {}),
        }
        vpc_data['subnets'].append(subnet_data)
    vpcs.append(vpc_data)
    
vms = []
for vm in data['vms']:
    vm_data = {
        'vmid': new_tenant['id'] + str(random.randint(0, 99)),
        'name': vm['name'],
        'state': 'requested',
        'memory': vm['memory'],
        'vcpu': vm['vcpu'],
        'capacity': vm['capacity'],
        'image_path': '',
        'interfaces': [],
    }
    for interface in vm['interfaces']:
        interface_data = {
            'name': interface['name'],
            'subnet': interface['subnet'],
            'dhcp': interface.get('dhcp', False),
            'ipaddr': interface.get('ipaddr', ''),
        }
        vm_data['interfaces'].append(interface_data)
    vms.append(vm_data)

with open('master_db_northbound_effect.yaml', 'r') as f:
    master_data = yaml.safe_load(f)

for tenant in master_data['tenants']:
    if tenant['name'] == org_name:
        tenant['vpcs'] += vpcs
        tenant['vms'] += vms
        break
else:
    new_tenant['vpcs'] = vpcs
    new_tenant['vms'] = vms
    master_data['tenants'].append(new_tenant)

with open('master_db_northbound_effect.yaml', 'w') as f:
    yaml.dump(master_data, f)
