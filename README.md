# Quicklyv2
## Quickly CDN Service Readme

## We have comined our main detailed ReadMe and Report, the ReadMe is as same as the "The Demo" section of the report

Quickly is a Content Delivery Network (CDN) service that deploys infrastructure on a Linux machine and provides tenant isolation. This readme is intended for service providers who will be using the service internally and need to understand its internal workings.

Required:
Ansible, OvSwitch, Python, Docker, Libvirt, Virsh, etcd

Once the input has been given, the northboundVerifier is run,
python3 northboundVerifier.py <yaml file>

if [OK] in all output, then move to running the northbound.py
python2 northbound.py <yaml_file>

Then the etcd database is populated

## Conclusion

Thank you for choosing the Quickly CDN service. If you have any questions or issues, please contact our support team at support@quicklycdn.com.

