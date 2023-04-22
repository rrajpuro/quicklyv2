import yaml
import etcd3
from pprint import pprint as pp

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


e = etcd3.client()
db = e.get_all()

res = convert_to_dict(db)

# with open('sample_master_db.yaml', 'r') as f:
#     data = yaml.safe_load(f)

# res = convert_to_kv_pairs(data)

# for k,v in res:
#     e.put(k,v)

pass