__author__ = 'arkilic'
import time
import random
from metadataStore.dataapi.commands import save_header, insert_event_descriptor, save_beamline_config, insert_event
from metadataStore.dataapi.commands import find, find_last
from pprint import pprint

h_id = random.randint(0, 200000)
h_id2 = random.randint(0, 200000)

bc_id = random.randint(0, 450000)
ev_d_id = random.randint(0, 200000)
start = time.time()
save_header(beamline_id='csx29', scan_id=h_id, tags=['arman', 123])
end = time.time()
print('Header insert time is ' + str((end-start)*1000) + ' ms')

start = time.time()
insert_event_descriptor(scan_id=h_id, event_type_id=1, descriptor_name='myscan', data_keys=['armanarkilic.VAL'])
end = time.time()
print('Descriptor insert time is ' + str((end-start)*1000) + ' ms')

start = time.time()
hdr3 = save_beamline_config(scan_id=h_id, config_params={'nam1': 'val'})
end = time.time()

start = time.time()
insert_event(scan_id=h_id, descriptor_name='myscan', owner='arkilic', seq_no=0, data={'armanarkilic.VAL':'value'})
end = time.time()
print('Event insert time is ' + str((end-start)*1000) + ' ms')

sample_result = find(owner='arkilic', data=True)
print sample_result.keys()
print sample_result['header_0']['event_descriptors']['event_descriptor_0']


start = time.time()
insert_event_descriptor(scan_id=h_id, event_type_id=1, descriptor_name='my_new_scan', data_keys=['armanarkilic.RBV',
                                                                                                 'armanarkilic.VAL'])
end = time.time()
print('Descriptor insert time is ' + str((end-start)*1000) + ' ms')

start = time.time()
hdr3 = save_beamline_config(scan_id=h_id, config_params={'nam1': 'val'})
end = time.time()

start = time.time()
insert_event(scan_id=h_id, descriptor_name='my_new_scan', owner='arkilic', seq_no=0, data={'armanarkilic.VAL': 'value1',
                                                                                           'armanarkilic.RBV': 'value2'})
end = time.time()
print('Event insert time is ' + str((end-start)*1000) + ' ms')

sample_result = find(owner='arkilic', data=True)



pprint(find_last()[0])