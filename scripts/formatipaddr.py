import json
import subprocess
import sys

allFlag = True

stdin = (sys.stdin.read())

# get output
output = json.loads(stdin)

res = [['Interface name', 'MAC Address', 'IP address']]

for inf in output:
    for addr in inf['addr_info']:
        if allFlag:
            try:
                res.append([inf['ifname'], inf['address'], addr['local']])
            except:
                res.append([inf['ifname'], inf['address']])
        else:
            try:
                if addr['family'] == 'inet':
                    res.append([inf['ifname'], inf['address'], addr['local']])
            except:
                pass

# Determine column widths
col_widths = [max(len(str(row[i])) for row in res) for i in range(len(res[0]))]

# Print table
for k, row in enumerate(res):
    if k == 1:
        print('-'*sum(col_widths))
    for i in range(len(row)):
        print(str(row[i]).ljust(col_widths[i]), end='  ')
    print()
