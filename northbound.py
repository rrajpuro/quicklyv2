import yaml
import random 
import json
import etcd3

with open('customer_input_template_red.yaml', 'r') as f:
    data = yaml.safe_load(f)
e = etcd3.client()

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
            result.append((f"{prefix}{k}", v))
    return result

org_name = data['name']
vpcs = {}
get_tip = data['vpcs']

new_tenant = {
    'id': str(random.randint(10, 99)),
    'name': org_name,
    'state': 'requested',
    'logging': data['logging']

}
pip = "192.168.10." + str(random.randint(1, 254)) 
octets = pip.split('.')
last_octet = int(octets[-1])
next_octet = last_octet + 1
cip = f"{octets[0]}.{octets[1]}.{octets[2]}.{next_octet}"

for vpc in data['vpcs']:
    vpcid =  new_tenant['id'] + str(random.randint(0, 99))
    trunc_vpc_id = vpcid[-2:]
    fourths_octet = random.randint(0, 255)
    
    vpc_data = {
        'vpcid':vpcid,
        'name': vpc['name'],
        'location': vpc['location'],
        'pip':pip + "/24",  
        'cip': cip+ "/24",
        'tip': f"10.0.{trunc_vpc_id}.{fourths_octet}", 
        'tipremote':f"10.0.{trunc_vpc_id}.{fourths_octet+1}",
        'state': 'requested',
        'cdn': {},
        'subnets': {},
        'containers': {}
    }
    if 'cdn' in vpc:
        cdn = vpc['cdn']

        cdn_data = {
            'state': 'requested',
            'cdndomainname': cdn['cdndomainname'],
            'ha': cdn['ha'],
            'primaryip':cdn['primaryip'],
            'secondaryip':cdn['secondaryip'],
            'origin':cdn['origin'],
            'originport':cdn['originport']
        }
        vpc_data['cdn'] = cdn_data
    if 'subnets' in vpc:
        for subnet in vpc['subnets']:
            subnet_data = {
                'subid': vpc_data['vpcid'] + str(random.randint(0, 99)),
                'state':'requested',
                'name': subnet['name'],
                'mode': subnet['mode'],
                'gateway': subnet['gateway'],
            }
            vpc_data['subnets'][subnet_data['subid']] = subnet_data
    if 'containers' in vpc:
        for container in vpc.get('containers', []):
            container_data = {
                'containerid': vpc_data['vpcid'] + str(random.randint(100, 200)),
                'name': container['name'],
                'state': 'requested',
                'image': container.get('image', 'ubuntu'),
                'interfaces': {},
            }
            for interface in container['interfaces']:
                interface_data = {
                    'name': interface['name'],
                    'subnet': interface['subnet'],
                    'ipaddr': interface.get('ipaddr', ''),
                    'gateway': interface.get('gateway','')
                }
                container_data['interfaces'][interface['name']] = interface_data
            vpc_data['containers'][container_data['containerid']] = container_data

    vpcs[vpc['name']] = vpc_data



output = {'tenants': {new_tenant['id']: {'name': new_tenant['name'], 'logging': new_tenant['logging'], 'state': new_tenant['state'], 'vpcs': {vpc_data['vpcid']: vpc_data for vpc_data in vpcs.values()}}}}
json_output = json.dumps(output)
output_dict = json.loads(json_output)
kvpairs = convert_to_kv_pairs(output_dict)
# print(output_dict)

for k, v in kvpairs:
    e.put(k, str(v))



#Retrieve Everything

# e.delete_prefix('/')

db = e.get_all()
retrieved_info = convert_to_dict(db)
print(retrieved_info)