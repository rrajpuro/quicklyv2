#!/usr/bin/env python3

import yaml
import ipaddress
import sys

def checkVPCNames(data):
    names = []
    for vpc in data["vpcs"]:
        names.append(vpc["name"])
    if len(names) != len(set(names)):
        return "[E] Name Conflict found in VPCs (0x10)"
    else:
        return "[OK] VPC Names (0x00)"

def checkVPCSubnets(data):
    subnetNames = []
    for vpc in data["vpcs"]:
        for subnet in vpc["subnets"]:
            subnetNames.append(subnet["name"])
    if len(subnetNames) != len(set(subnetNames)):
        return "[E] Subnet Name Conflict found in VPC (0x1a)"
    else:
        return "[OK] Subnet Name (0x00)"+"+"+str(subnetNames)
    
def checkVPCSubnetMode(data):
    flag = False
    for vpc in data["vpcs"]:
        for subnet in vpc["subnets"]:
            if subnet["mode"] not in ["nat", "route"]:
                flag = True
                break
    if flag:
        return "[E] Choose nat/route Network Mode (0x1b)"
    else:
        return "[OK] Network Mode (0x00)"

def findIPRange(network):
    f1,f2,f3,f4=network.split('.')
    f4,m=f4.split('/')

    f1,f2,f3,f4,m=int(f1),int(f2),int(f3),int(f4),int(m)
    l1,l2,l3,l4=f1,f2,f3,f4

    if(m==8):
        f2=f3=f4=0

        l2=l3=255
        l4=254
    elif(m==16):
        f3=f4=0

        l3=255
        l4=254
    elif(m==24):
        f4=0
        l4=254
    elif(m>0 and m<8):
        binO1=bin(f1).replace("0b","").rjust(8,"0")
       
        decO1=binO1[:m].ljust(8,"0")
        f1=int(decO1,2)
        f2=f3=f4=0

        decL1=binO1[:m].ljust(8,"1")
        l1=int(decL1, 2)
        l2=l3=255
        l4=254
    elif(m>8 and m<16):
        bitsToNullify=m-8
        binO2=bin(f2).replace("0b","").rjust(8,"0")
        
        decO2=binO2[:bitsToNullify].ljust(8,"0")
        f2=int(decO2,2)
        f3=f4=0

        decL2=binO2[:bitsToNullify].ljust(8,"1")
        l2=int(decL2,2)
        l3=255
        l4=254

    elif(m>16 and m<24):
        bitsToNullify=m-16
        binO3=bin(f3).replace("0b","").rjust(8,"0")
       
        decO3=binO3[:bitsToNullify].ljust(8,"0")
        f3=int(decO3,2)
        f4=0

        decL3=binO3[:bitsToNullify].ljust(8,"1")
        l3=int(decL3,2)
        l4=254
    else:
        bitsToNullify=m-24
        
        binO4=bin(f4).replace("0b","").rjust(8,"0")
        decO4=binO4[:bitsToNullify].ljust(8,"0")
        f4=int(decO4,2)

        decL4=binO4[:bitsToNullify].ljust(8,"1")
        l4=int(decL4,2)

    network=str(f1)+"."+str(f2)+"."+str(f3)+"."+str(f4)+"/"+str(m)
    last=str(l1)+"."+str(l2)+"."+str(l3)+"."+str(l4)+"/"+str(m)

    return network+"+"+last

def masterCheckIP(ipList):
    check = True
    final=""
    try:
        for ip in ipList:
            ipaddress.ip_address(ip.split("/")[0])
    except ValueError:
        check = False

    if check:
        for ip in ipList:
            final = final + "+" + findIPRange(ip)
        return "i0"+final
    else:
        return "i1"

def checkVPCSubnetGatewayIP(data):
    dup = False
    gatewayIPList = []
    for vpc in data["vpcs"]:
        for subnet in vpc["subnets"]:
            gatewayIPList.append(subnet["gateway"])
        print(gatewayIPList)
        if len(gatewayIPList) != len(set(gatewayIPList)):
            dup = True
            break
        else:
            ans = masterCheckIP(gatewayIPList)
            print(ans)
            if "i1" in ans:
                return "[E] Wrong IP Format (0x1c)"
            else:
                if (ipaddress.ip_address(subnet["dhcp"]["start"]) not in ipaddress.ip_network(ans.split("+")[1])) or (ipaddress.ip_address(subnet["dhcp"]["end"]) not in ipaddress.ip_network(ans.split("+")[1])):
                    return "[E] IP Address not in range (0x1cc)"
            gatewayIPList = []
    if dup:
        return "[E] Conflicting Gateway IPs in a VPC (0xd)"
    return "[OK] Correct IP Format (0x00)"

def checkVMNames(data):
    flag = False
    names = []
    for vpc in data["vpcs"]:
        for vms in vpc["vms"]:
            names.append(vms["name"])
        if len(names) != len(set(names)):
            flag = True
            break
        else:
            names = []
    if flag:
        return "[E] Conflicting VM Names (0xe)"
    else:
        return "[OK] VM Names (0x00)"

def checkVMIntNames(data):
    flag = False
    vmIntNames = []
    for vpc in data["vpcs"]:
        for vms in vpc["vms"]:
            for inter in vms["interfaces"]:
                vmIntNames.append(inter["name"])
            if len(vmIntNames) != len(set(vmIntNames)):
                flag = True
                break
            else:
                vmIntNames = []
    if flag:
        return "[E] Conflict in VM's Interface Names (0x1f)"
    else:
        return "[OK] VM's Interface Names (0x00)"

def checkVMSubnet(data):
    flag = False
    subnetNames = []
    for vpc in data["vpcs"]:
        for subnets in vpc["subnets"]:
            subnetNames.append(subnets["name"])
        for vms in vpc["vms"]:
            for subnet in vms["interfaces"]:
                if subnet["subnet"] not in subnetNames:
                    flag = True
                    break
        subnetNames = []
    if flag:
        return "[E] VM's Network not present in VPC (0x20)"
    else:
        return "[OK] VM's Network present in VPC (0x00)"

def checkVMIntDorS(data):
    flag = False
    for vpc in data["vpcs"]:
        for vms in vpc["vms"]:
            for inter in vms["interfaces"]:
                if "dhcp" in inter.keys() and "ipaddr" in inter.keys():
                    flag = True
                    break
    if flag:
        return "[E] Conflicting config for VM's interface, found both DHCP and Static! (0x21)"
    else:
        return "[OK] VM's interface Config (0x00)"

def masterCheck(data):
    errorCodes=[]
    try:
        errorCodes.append(checkVPCNames(data))
        cS=checkVPCSubnets(data)
        errorCodes.append(cS.split("+")[0])
        errorCodes.append(checkVPCSubnetMode(data))
        errorCodes.append(checkVPCSubnetGatewayIP(data))

        errorCodes.append(checkVMNames(data))
        errorCodes.append(checkVMIntNames(data))
        errorCodes.append(checkVMSubnet(data))
        errorCodes.append(checkVMIntDorS(data))
    except KeyError:
        errorCodes.append("[EE] Key Error, please check the YAML file, invalid/unknown key encountered (0xff)")

    return errorCodes

def masterError():
    return "[EE] Key Error, please check the YAML file, invalid/unknown key encountered (0xff)"

if __name__ == "__main__":
    args = sys.argv
    with open(args[1], "r") as stream:
        try:
            data = yaml.safe_load(stream)
            print(masterCheck(data))
        except yaml.YAMLError as exc:
            print(masterError())