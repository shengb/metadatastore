__author__ = 'arkilic'

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from metadataStore.config.parseConfig import database, host, port
from metadataStore.sessionManager.databaseLogger import DbLogger


conn = MongoClient(host='xf23id-broker', port=27017)
db = conn['metaDataStore']


metadataLogger = DbLogger(db_name=database, host=host, port=int(port))
