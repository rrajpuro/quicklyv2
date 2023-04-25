import yaml
import etcd3
import threading
import time
from pprint import pprint as pp
from controllerv2 import maincon

def controller(etcdc):
    print('Hi! watch function triggered me')
    time.sleep(10)
    # Calling the configuration script
    maincon(etcdc)
    global watch_count
    watch_count = 0
    print('Controller configuration Done!')
    return

if __name__=='__main__':

    etcd = etcd3.client()

    # watch prefix
    watch_count = 0
    events_iterator, cancel = etcd.watch_prefix("/")
    print('----- Watching etcd for changes -----')
    for event in events_iterator:
        print('watch')
        print(watch_count)
        print(event)
        if watch_count == 0:
            print('First watch')
            x = threading.Thread(target=controller, args=(etcd,))
            x.start()
        watch_count += 1

    db = etcd.get_all()
