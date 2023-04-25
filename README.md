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

Then the etcd database is populated,
Once done, we then go ahead to run the controller.py on the database.
  
  Before that, we recommend you to run our watchdog file called runner.py which gives you an insight on what is happening.
  
  Then, once you get a positive output, move ahead with testing the CDN nodes!

Our system is robust, you can check the State of the CDN nodes using this command:
  ./scripts/etcdshow.sh --regex '.*state.*|.*name.*'
  
  Our system is robust, you can check the IP Addresses of the CDN nodes using this command:
  ./scripts/etcdshow.sh --regex '.*ip.*|.*name.*'

  Then test the CDN by:
  curl <ip>:port
  
  and then check the logs by tapping into the logging server (if opted by the customer) and then see the logs by
  cat logfile.csv
  
## Conclusion

Thank you for choosing the Quickly CDN service. If you have any questions or issues, please contact our support team at support@quicklycdn.com.

