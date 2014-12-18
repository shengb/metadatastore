__author__ = ['arkilic','edill']
import six
import random
import time
from pprint import pprint
from metadataStore.api.collection import (create_event,
                                          create_header,
                                          create_event_descriptor,
                                          find_last, find, find2)
from metadataStore.api.collection import search_and_compose as search
import numpy as np
from metadataStore.sessionManager import databaseInit
from pymongo import MongoClient
from metadataStore.config.parseConfig import port, database
from metadataStore.sessionManager.databaseLogger import DbLogger
from metadataStore.api.analysis import find

s_id = random.randint(0, 10000)

nested_list = [pprint, [pprint, [pprint, [pprint, pprint]]]]
nested_dict = list(six.itervalues(find(find_last()[0]['_id'])))[0]
# nested_dict = {}
header={'scan_id': s_id,
        'tags': ['synthetic', 'edill'],
        'custom': {
            'dict': {'a': 1, 'nested': nested_dict},
            'list': ['a', 'b', 1, nested_list],
            'string': 'cat',
            'float': 3.1415,
            'int': 42,
            'tuple': (1, 2, 3),
            # non-standard keys that create_header should bash to a string
            'np': np,
            'time': time,
            'tuple': (1, 2, 3, 4),
        }}

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

x_range = np.arange(0, .02, .01)
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
    time.sleep(0.1)
    print('scan_id: {}. step {} of {}'.format(s_id, idx+1, len(x_range)))
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
pprint(find(scan_id='last', data=True))
pprint("Header from find(scan_id=s_id)")
pprint(find(scan_id=s_id, data=True))

pprint("Header from find2(scan_id=s_id)")

pprint(find2(scan_id=s_id, data=True))