#!/usr/bin/env python3

import yaml
import ipaddress
import sys

def checkVPCNames(data):
    names = []
    for vpc in data["vpcs"]:
        names.append(vpc["name"])
    if len(names) != len(set(names)):
        return "\t[E] Name Conflict found in VPCs (0x10)"
    else:
        return "[OK] VPC Names valid (0x00)"

def checkVPCSubnets(data):
    subnetNames = []
    for vpc in data["vpcs"]:
        if "subnets" in vpc.keys():
            for subnet in vpc["subnets"]:
                subnetNames.append(subnet["name"])
    if len(subnetNames) != len(set(subnetNames)):
        return "\t[E] Subnet Name Conflict found in VPC (0x1a)"
    else:
        return "[OK] VPC Subnet Name valid (0x00)"+"+"+str(subnetNames)
    
def checkVPCSubnetMode(data):
    flag = False
    for vpc in data["vpcs"]:
        if "subnets" in vpc.keys():
            for subnet in vpc["subnets"]:
                if subnet["mode"] not in ["nat", "route"]:
                    flag = True
                    break
    if flag:
        return "\t[E] Network Mode invalid! (nat/route) (0x1b)"
    else:
        return "[OK] Network Mode valid (0x00)"

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

def ipValidator(ipList):
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
        if "subnets" in vpc.keys():
            for subnet in vpc["subnets"]:
                gatewayIPList.append(subnet["gateway"])
            if len(gatewayIPList) != len(set(gatewayIPList)):
                dup = True 
                break
            else:
                ans = ipValidator(gatewayIPList)
                if "i1" in ans:
                    return "\t[E] Wrong IP Format (0x1c)"
                else:
                    if "dhcp" in subnet.keys():
                        if (ipaddress.ip_address(subnet["dhcp"]["start"]) not in ipaddress.ip_network(ans.split("+")[1])) or (ipaddress.ip_address(subnet["dhcp"]["end"]) not in ipaddress.ip_network(ans.split("+")[1])):
                            return "\t[E] IP Address not in range (0x1cc)"
                gatewayIPList = []
    if dup:
        return "\t[E] Conflicting Gateway IPs in a VPC (0x1d)"
    
    return "[OK] VPC IP Format valid (0x00)"

def checkContainerNames(data):
    flag = False
    names = []
    for vpc in data["vpcs"]:
        if "containers" in vpc.keys():
            for vms in vpc["containers"]:
                names.append(vms["name"])
            if len(names) != len(set(names)):
                flag = True
                break
            else:
                names = []
    if flag:
        return "\t[E] Conflicting Container Names (0x1e)"
    else:
        return "[OK] Container Names valid (0x00)"

def checkContainerIntNames(data):
    flag = False
    vmIntNames = []
    for vpc in data["vpcs"]:
        if "containers" in vpc.keys():
            for vms in vpc["containers"]:
                for inter in vms["interfaces"]:
                    vmIntNames.append(inter["name"])
                if len(vmIntNames) != len(set(vmIntNames)):
                    flag = True
                    break
                else:
                    vmIntNames = []
    if flag:
        return "\t[E] Container Interface Names Conflict! (0x1f)"
    else:
        return "[OK] Container Interface Names valid (0x00)"

def checkContainerSubnet(data):
    flag = False
    subnetNames = []
    for vpc in data["vpcs"]:
        if "subnets" in vpc.keys():
            for subnets in vpc["subnets"]:
                subnetNames.append(subnets["name"])
            for vms in vpc["containers"]:
                for subnet in vms["interfaces"]:
                    if subnet["subnet"] not in subnetNames:
                        flag = True
                        break
            subnetNames = []
    if flag:
        return "\t[E] Container Network not present in VPC (0x20)"
    else:
        return "[OK] Container Network presence valid (0x00)"

def checkContainerIntDorS(data):
    flag = ""
    for vpc in data["vpcs"]:
        if "containers" in vpc.keys():
            for vms in vpc["containers"]:
                for inter in vms["interfaces"]:
                    if "dhcp" in inter.keys() and "ipaddr" in inter.keys():
                        flag = "conflict"
                        break
                    elif "ipaddr" in inter.keys():
                        ip = inter["ipaddr"]
                        try:
                            ipaddress.ip_address(ip.split("/")[0])
                        except ValueError:
                            flag = "locha"
                            break
    
    if flag == "conflict":
        return "\t[E] Container interface conflict! Found both DHCP and Static! (0x21)"
    elif flag == 'locha':
        return "\t[E] Container interface IP is invalid! (0x22)"
    else:
        return "[OK] Container interface configuration valid (0x00)"

def checkCDNDetails(data):
    flag = ""
    haIPList = []
    for vpc in data["vpcs"]:
        if "cdn" in vpc.keys():
            if vpc["cdn"]["cdndomainname"] == None:
                flag = "name"
                break
            if vpc["cdn"]["ha"] == 'true':
                haIPList.append(vpc["cdn"]["primaryip"])
                haIPList.append(vpc["cdn"]["secondaryip"])
                if len(haIPList) != len(set(haIPList)):
                    flag = "haipsame"
                    break
            if vpc["cdn"]["origin"] == None:
                flag = "nooriginip"
                break
            if vpc["cdn"]["originport"] == None:
                flag = "nooriginport"
                break

    if flag == "name":
        return "\t[E] No name in CDN Domain Name (0x23)"
    elif flag == "haipsame":
        return "\t[E] CDN HA IP Conflict! (0x24)"
    elif flag == "nooriginip":
        return "\t[E] CDN Origin IP Missing! (0x25)"
    elif flag == "nooriginport":
        return "\t[E] CDN Origin Port Missing! (0x26)"
    else:
        return "[OK] CDN details valid (0x00)"

def masterCheck(data):
    errorCodes=[]
    try:
        errorCodes.append(checkVPCNames(data))
        cS=checkVPCSubnets(data)
        errorCodes.append(cS.split("+")[0])
        errorCodes.append(checkVPCSubnetMode(data))
        errorCodes.append(checkVPCSubnetGatewayIP(data))

        errorCodes.append(checkContainerNames(data))
        errorCodes.append(checkContainerIntNames(data))
        errorCodes.append(checkContainerSubnet(data))
        errorCodes.append(checkContainerIntDorS(data))
        errorCodes.append(checkCDNDetails(data))
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
            for i in masterCheck(data):
                print(i)
        except yaml.YAMLError as exc:
            print(masterError())