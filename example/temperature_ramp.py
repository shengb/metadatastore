from __future__ import division
from metadatastore import (insert_event, insert_event_descriptor,find_events)
import numpy as np
import common

# "Magic numbers" for this simulation
start, stop, step, points_per_step = 0, 3, 1, 7
deadband_size = 0.9
num_exposures = 23

@common.example
def run(run_start_uid=None, sleep=0):
    if sleep != 0:
        raise NotImplementedError("A sleep time is not implemented for this "
                                  "example.")
    # Make the data
    ramp = common.stepped_ramp(start, stop, step, points_per_step)
    deadbanded_ramp = common.apply_deadband(ramp, deadband_size)
    rs = np.random.RandomState(5)
    point_det_data = rs.randn(num_exposures)

    # Create Event Descriptors
    data_keys1 = {'point_det': dict(source='PV:ES:PointDet', dtype='number')}
    data_keys2 = {'Tsam': dict(source='PV:ES:Tsam', dtype='number')}
    ev_desc1_uid = insert_event_descriptor(run_start=run_start_uid,
                                           data_keys=data_keys1, time=0.)
    ev_desc2_uid = insert_event_descriptor(run_start=run_start_uid,
                                           data_keys=data_keys2, time=0.)

    # Create Events.
    events = []

    # Point Detector Events
    for i in range(num_exposures):
        time = float(i + 0.01 * rs.randn())
        data = {'point_det': (point_det_data[i], time)}
        event_dict = dict(descriptor=ev_desc1_uid, seq_num=i,
                          time=time, data=data)
        event_uid = insert_event(**event_dict)
        # grab the actual event from metadatastore
        event, = find_events(uid=event_uid)
        events.append(event)

    # Temperature Events
    for i, (time, temp) in enumerate(zip(*deadbanded_ramp)):
        time = float(time)
        data = {'Tsam': (temp, time)}
        event_dict = dict(descriptor=ev_desc2_uid, time=time,
                          data=data, seq_num=i)
        event_uid = insert_event(**event_dict)
        event, = find_events(uid=event_uid)
        events.append(event)

    #todo insert run stop if run_start_uid is not None

    return events


if __name__ == '__main__':
    import metadatastore as mdsc
    blc_uid = mdsc.insert_beamline_config({}, time=0.)
    run_start_uid = mdsc.insert_run_start(scan_id=3022013,
                                          beamline_id='testbed',
                                          beamline_config=blc_uid,
                                          owner='tester',
                                          group='awesome-devs',
                                          project='Nikea',
                                          time=0.)

    print('beamline_config_uid = %s' % blc_uid)
    print('run_start_uid = %s' % run_start_uid)
    run(run_start_uid)
