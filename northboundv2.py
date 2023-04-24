import yaml
import random 
import json
import etcd3
import argparse
import re

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

def quicklyparser(filename):
    with open(filename, 'r') as f:
        data = yaml.safe_load(f)

    org_name = data['name']
    
    check_orgname(org_name)

    vpcs = {}
    get_tip = data['vpcs']

    new_tenant = {
        'id': f'{random.randint(0, 99):02d}',
        'name': org_name,
        'state': 'requested',
        'logging': data['logging']

    }

    for vpc in data['vpcs']:
        vpcnum = f'{random.randint(0, 99):02d}'
        vpcid =  new_tenant['id'] + vpcnum
        pip = f"172.1{new_tenant['id']}.{vpcnum}.2"
        cip = f"172.1{new_tenant['id']}.{vpcnum}.1"
        
        vpc_data = {
            'vpcid':vpcid,
            'name': vpc['name'],
            'location': vpc['location'],
            'pip':pip + "/24",  
            'cip': cip+ "/24",
            'tip': f"10.0.{vpcnum}.1/24",
            'tipremote': f"10.0.{vpcnum}.2/24",
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
                'origin':cdn['origin'],
                'originport':cdn['originport']
            }
            if cdn['ha'] == 'True':
                cdn_data = {'secondaryip':cdn['secondaryip'], **cdn_data}
            vpc_data['cdn'] = cdn_data
        if 'subnets' in vpc:
            for subnet in vpc['subnets']:
                subnetnum = f'{random.randint(0, 99):02d}'
                subnet_data = {
                    'subid': vpc_data['vpcid'] + subnetnum,
                    'state':'requested',
                    'name': subnet['name'],
                    'mode': subnet['mode'],
                    'gateway': subnet['gateway'],
                }
                vpc_data['subnets'][subnet_data['subid']] = subnet_data
        if 'containers' in vpc:
            for container in vpc.get('containers', []):
                connum = f'{random.randint(0, 99):02d}'
                container_data = {
                    'containerid': vpc_data['vpcid'] + connum,
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


    output = {
        'tenants': {
            new_tenant['id']: {
                'name': new_tenant['name'],
                'logging': new_tenant['logging'],
                'state': new_tenant['state'],
                'vpcs': {
                    vpc_data['vpcid']: vpc_data for vpc_data in vpcs.values()
                }
            }
        }
    }

    json_output = json.dumps(output)
    output_dict = json.loads(json_output)
    return output_dict

def check_orgname(name):
    e = etcd3.client()
    db = e.get_all()
    for value, meta in db:
        value = value.decode("utf-8")
        key = meta.key.decode("utf-8")
        # print(f'Checked {key}:{value}')
        if re.search(r'/tenants/\d+/name',key) and value == name:
            print(f'Error: Key {key} already exists with value {value}. Provide a new value for Organization name.')
            exit(0)
    return

if __name__=='__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Load YAML file into etcd')
    parser.add_argument('yaml_file', type=str, nargs='?', default=None, help='Path to YAML file')
    args = parser.parse_args()

    if args.yaml_file is None:
        parser.print_help()
        exit(0)
    else:
        # Load YAML file
        output_dict = quicklyparser(args.yaml_file)
        # print(output_dict)

    kvpairs = convert_to_kv_pairs(output_dict)

    e = etcd3.client()
    for k, v in kvpairs:
        current_value, _ = e.get(k)
        if current_value is not None:
            print(f'Warning: key {k} already exists with value {current_value}. Overwriting with new value {v}.')
        e.put(k, str(v))

    #Delete Everything
    # e.delete_prefix('/')

    #Retrieve Everything
    # db = e.get_all()
    # retrieved_info = convert_to_dict(db)
    # print(retrieved_info)