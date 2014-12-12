__author__ = ['arkilic','edill']
import six
import random
import time
from pprint import pprint
from metadataStore.api.collection import (create_event,
                                          create_header,
                                          create_event_descriptor,
                                          find_last, find)
from metadataStore.api.collection import search_and_compose as search
import numpy as np

s_id = random.randint(0, 10000)

header={'scan_id': s_id, 'tags': ['synthetic', 'edill']}

create_header(**header)

data = {'motor': 0, 'img_sum': 0, 'time': time.time()}

desc_name = 'cosine_scan'
ev_desc1 = {'scan_id': s_id,
            'descriptor_name': desc_name,
            'event_type_id': 42,
            'tag': 'experimental',
            'data_keys': list(six.iterkeys(data))
}
create_event_descriptor(**ev_desc1)

x_range = np.arange(0, .03, .01)
for idx, x in enumerate(x_range):
    data['motor'] = x
    data['img_sum'] = np.sin(x)
    data['time'] = time.time()
    event = {'scan_id': s_id,
             'descriptor_name': desc_name,
             'seq_no': idx,
             'data': data
    }
    create_event(event)
    time.sleep(0.01)
# find_last()
# print('scan_id: {}'.format(s_id))
#

pprint("Header")
pprint(find_last()[0])
pprint('==============')
pprint("Event_descriptor")
pprint(find_last()[1][0])
pprint('==============')
pprint("Events")
pprint(find_last()[2][0])
pprint(find_last()[2][1])


pprint("Header from find(scan_id=last)")
pprint(find(scan_id='last'))
pprint("Header from find(scan_id=s_id)")
pprint(find(scan_id=s_id))