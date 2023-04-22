import json
import subprocess
import sys
import select

if len(sys.argv) > 1 and sys.argv[1] == 'all':
    allFlag = True
else:
    allFlag = False
# Check if stdin is available
if select.select([sys.stdin,],[],[],0.0)[0]:
    res = sys.stdin.read()
else:
    # run shell script
    result = subprocess.run(['ip', '--json', 'addr'], stdout=subprocess.PIPE)
    res = result.stdout.decode('utf-8')

# get output
output = json.loads(res)

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
