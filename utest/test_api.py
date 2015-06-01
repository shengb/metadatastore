# Smoketest the api

from metadatastore import find_events
from metadatastore import find_event_descriptors
from metadatastore import find_beamline_configs
from metadatastore import find_run_starts
from metadatastore import find_run_stops
from metadatastore import find_last
from metadatastore import insert_event
from metadatastore import insert_event_descriptor
from metadatastore import insert_run_start
from metadatastore import insert_beamline_config
from metadatastore import insert_run_stop
from metadatastore import EventDescriptorIsNoneError
from metadatastore import format_events
from metadatastore import format_data_keys
from metadatastore import db_connect
from metadatastore import db_disconnect
from metadatastore import Document


if __name__ == "__main__":
    import nose
    nose.runmodule(argv=['-s', '--with-doctest'], exit=False)
