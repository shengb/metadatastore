__author__ = 'arkilic'
import datetime
import getpass
from metadataStore.dataapi.commands import save_header, save_beamline_config, insert_event_descriptor, insert_event
from metadataStore.dataapi.commands import save_bulk_header
from metadataStore.dataapi.commands import find, get_event_descriptor_hid_edid, db
from metadataStore.utilities import get_scan_id


def create(header=None, beamline_config=None, event_descriptor=None):
    """
    Create header, beamline_config, and event_descriptor given dictionaries with appropriate name-value pairs.

    :param header: Header attribute-value pairs
    :type header: dict

    :param beamline_config: BeamlineConfig attribute-value pairs
    :type beamline_config: dict

    :param event_descriptor: EventDescriptor attribute-value pairs
    :type event_descriptor: dict

    :raises: TypeError, ValueError, ConnectionFailure, NotUniqueError

    :returns: None

    Usage:

    >>> sample_header = {'scan_id': 1234}
    >>> create(header=sample_header)

    >>> create(header={'scan_id': 1235, 'start_time': datetime.datetime.utcnow(), 'beamline_id': 'my_beamline'})

    >>> create(header={'scan_id': 1235, 'start_time': datetime.datetime.utcnow(), 'beamline_id': 'my_beamline',
    ...                 'owner': 'arkilic'})

    >>> create(header={'scan_id': 1235, 'start_time': datetime.datetime.utcnow(), 'beamline_id': 'my_beamline',
    ...                 'owner': 'arkilic', 'custom': {'attribute1': 'value1', 'attribute2':'value2'}})

    >>> create(beamline_config={'scan_id': s_id})

    >>> create(event_descriptor={'scan_id': s_id, 'descriptor_name': 'scan', 'event_type_id': 12, 'tag': 'experimental'})

    >>> create(event_descriptor={'scan_id': s_id, 'descriptor_name': 'scan', 'event_type_id': 12, 'tag': 'experimental',
    ...                          'type_descriptor':{'attribute1': 'value1', 'attribute2': 'value2'}})

    >>> sample_event_descriptor={'scan_id': s_id, 'descriptor_name': 'scan', 'event_type_id': 12, 'tag': 'experimental',
    ...                          'type_descriptor':{'attribute1': 'value1', 'attribute2': 'value2'}})
    >>> sample_header={'scan_id': 1235, 'start_time': datetime.datetime.utcnow(), 'beamline_id': 'my_beamline',
    ...                 'owner': 'arkilic', 'custom': {'attribute1': 'value1', 'attribute2':'value2'}})
    >>> create(event_descriptor=sample_event_descriptor, header=sample_header)

    >>> create(beamline_config={'scan_id': 1234})

    >>> create(beamline_config={'scan_id': 1234, 'config_params': {'attribute1': 'value1', 'attribute2': 'value2'}})

    >>> sample_event_descriptor={'scan_id': s_id, 'descriptor_name': 'scan', 'event_type_id': 12, 'tag': 'experimental',
    ...                          'type_descriptor':{'attribute1': 'value1', 'attribute2': 'value2'}})
    >>> sample_header={'scan_id': 1235, 'start_time': datetime.datetime.utcnow(), 'beamline_id': 'my_beamline',
    ...                 'owner': 'arkilic', 'custom': {'attribute1': 'value1', 'attribute2':'value2'}})
    >>> sample_beamline_config = {'scan_id': 1234, 'config_params': {'attribute1': 'value1', 'attribute2': 'value2'}}
    >>> create(header=sample_header, event_descriptor=sample_event_descriptor, beamline_config=sample_beamline_config)

    """
    def parse_single_header(hdr):
        scan_id = get_scan_id(hdr, 'header')
        start_time = hdr.get('start_time', datetime.datetime.utcnow())
        header_owner = hdr.get('owner', getpass.getuser())
        beamline_id = hdr.get('beamline_id', None)
        custom = hdr.get('custom', {})
        tags = hdr.get('tags', [])
        status = hdr.get('status', 'In Progress')
        header_versions = hdr.get('header_versions', [])

        locals_ = locals()
        return dict((key, locals_[key]) for key in locals_.keys()
                    if key != 'hdr')

    if header is not None:
        if isinstance(header, dict):
            save_header(**parse_single_header(header))
        elif isinstance(header, list):
            header_list = [parse_single_header(hdr) for hdr in header]
            save_bulk_header(header_list=header_list)
        else:
            raise TypeError('Header must be a Python dictionary or list of Python dictionaries ')

    if beamline_config is not None:
        scan_id = get_scan_id(beamline_config, 'beamline_config')
        config_params = beamline_config.get('config_params', {})

        save_beamline_config(scan_id=scan_id, config_params=config_params)

    if event_descriptor is not None:
        scan_id = get_scan_id(event_descriptor, 'event_descriptor')
        event_type_id = event_descriptor.get('event_type_id', None)
        type_descriptor = event_descriptor.get('type_descriptor', {})
        tag = event_descriptor.get('tag', None)
        try:
            descriptor_name = event_descriptor['descriptor_name']
        except KeyError as ex:
            raise ValueError('%s is required for EventDescriptor' % ex.args[0])

        insert_event_descriptor(scan_id=scan_id, event_type_id=event_type_id, descriptor_name=descriptor_name,
                                type_descriptor=type_descriptor, tag=tag)


def record(event=dict()):
    """

    Events are saved given scan_id and descriptor name and additional optional parameters.

    Required fields: scan_id, descriptor_name

    Optional fields: owner, seq_no, data, description

    :param event: Dictionary used in order to save name-value pairs for Event entries
    :type event: dict

    :raises: ConnectionFailure, NotUniqueError, ValueError

    :returns: None

    Usage:

    >>> record(event={'scan_id': 1344, 'descriptor_name': 'ascan'})

    >>> record(event={'scan_id': 1344, 'descriptor_name': 'ascan', 'owner': 'arkilic', 'seq_no': 0,
                  ... 'data':{'motor1': 13.4, 'image1': '/home/arkilic/sample.tiff'}})

    >>> record(event={'scan_id': 1344, 'descriptor_name': 'ascan', 'owner': 'arkilic', 'seq_no': 0,
                  ... 'data':{'motor1': 13.4, 'image1': '/home/arkilic/sample.tiff'}},'description': 'Linear scan')
    """

    def parse_single_event(evt):
        scan_id = get_scan_id(evt, 'event')

        try:
            descriptor_name = evt['descriptor_name']
            seq_no = evt['seq_no']
        except KeyError as ex:
            raise ValueError('%s is required in order to record an event' % ex.args[0])

        description = evt.get('description', None)
        owner = evt.get('owner', getpass.getuser())
        data = evt.get('data', {})
        locals_ = locals()
        return dict((key, locals_[key]) for key in locals_.keys()
                    if key != 'evt')

    if isinstance(event, dict):
        evt = parse_single_event(event)
        insert_event(**evt)
    elif isinstance(event, list):
            bulk = db['event'].initialize_ordered_bulk_op()
            for single_event in event:
                composed_dict = parse_single_event(single_event)
                header_id, descriptor_id = get_event_descriptor_hid_edid(single_event['descriptor_name'],
                                                                         single_event['scan_id'])
                composed_dict['header_id'] = header_id
                composed_dict['descriptor_id'] = descriptor_id
                bulk.insert(composed_dict)
            bulk.execute()


def search(scan_id=None, owner=None, start_time=None, beamline_id=None, end_time=None, data=False,
           header_id=None, tags=None, num_header=50, event_classifier=dict()):
    """
    Provides an easy way to search Header entries inserted in metadataStore

    :param scan_id: Unique identifier for a given run
    :type scan_id: int

    :param owner: run header owner(unix user by default)
    :type owner: str

    :param start_time: Header creation time
    :type start_time: datetime.datetime object

    :param beamline_id: beamline descriptor
    :type beamline_id: str

    :param end_time: Header status time
    :type end_time: datetime.datetime object

    :param data: data field for collection routines to save experiemental progress
    :type data: dict

    :raises: TypeError, OperationError, ValueError

    :returns: Dictionary

    >>> search(scan_id=s_id)
    >>> search(scan_id=s_id, owner='ark*')
    >>> search(scan_id=s_id, start_time=datetime.datetime(2014, 4, 5))
    >>> search(scan_id=s_id, start_time=datetime.datetime(2014, 4, 5), owner='arkilic')
    >>> search(scan_id=s_id, start_time=datetime.datetime(2014, 4, 5), owner='ark*')
    >>> search(scan_id=s_id, start_time=datetime.datetime(2014, 4, 5), owner='arkili.')
    """
    result = find(scan_id=scan_id, owner=owner, start_time=start_time, beamline_id=beamline_id, end_time=end_time,
                  data=data, tags=tags, header_id=header_id, num_header=num_header, event_classifier=event_classifier)
    return result
