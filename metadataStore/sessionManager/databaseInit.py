__author__ = 'arkilic'

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from metadataStore.config.parseConfig import database, host, port
from metadataStore.sessionManager.databaseLogger import DbLogger


#TODO: Collapse this into sessionManager.__init__ for cleaner interface

conn = MongoClient(host=host, port=int(port))
db = conn[database]


metadataLogger = DbLogger(db_name=database, host=host, port=int(port))

