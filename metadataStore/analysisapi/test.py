__author__ = 'arkilic'

import random
from metadataStore.userapi.commands import create, record, search
import time
from metadataStore.analysisapi.utility import *

s_id = random.randint(0, 100000000000)
seq_n = random.randint(0, 10000)
print("s_id: {0}".format(s_id))
print("seq_n: {0}".format(seq_n))
create(header={'scan_id': s_id})
create(beamline_config={'scan_id': s_id})
create(event_descriptor={'scan_id': s_id, 'descriptor_name': 'scan', 'event_type_id': 12, 'tag': 'experimental'})
record(scan_id=s_id, descriptor_name='scan', seq_no=seq_n)
record(scan_id=s_id, descriptor_name='scan', seq_no=seq_n, data={'name': 'value'})

hdr1 = search(scan_id=s_id, data=True)
print hdr1
print get_data_keys(hdr1)
data_keys = get_data_keys(run_header=hdr1)
print listify(run_header=hdr1)