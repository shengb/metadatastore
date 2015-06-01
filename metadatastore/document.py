import six
from mongoengine.base.datastructures import BaseDict, BaseList
from mongoengine.base.document import BaseDocument
from bson.objectid import ObjectId
from bson.dbref import DBRef
from datetime import datetime
from itertools import chain
from collections import MutableMapping
import collections
from prettytable import PrettyTable
import humanize

__all__ = ['Document']


def _normalize(in_val, cache):
    """
    Helper function for cleaning up the mongoegine documents to be safe.

    Converts Mongoengine.Document to mds.Document objects recursively

    Converts:

     -  mongoengine.base.datastructures.BaseDict -> dict
     -  mongoengine.base.datastructures.BaseList -> list
     -  ObjectID -> str

    Parameters
    ----------
    in_val : object
        Object to be sanitized

    cache : dict-like
        Cache of already seen objects in the DB so that we do not
        have to de-reference and build them again.

    Returns
    -------
    ret : object
        The 'sanitized' object

    """
    if isinstance(in_val, BaseDocument):
        return Document.from_mongo(in_val, cache)
    elif isinstance(in_val, BaseDict):
        return {_normalize(k, cache): _normalize(v, cache)
                for k, v in six.iteritems(in_val)}
    elif isinstance(in_val, BaseList):
        return [_normalize(v, cache) for v in in_val]
    elif isinstance(in_val, ObjectId):
        return str(in_val)
    return in_val


class Document(MutableMapping):
    """A dictionary where d.key is the same as d['key']
    and attributes/keys beginning with '_' are skipped
    in iteration."""

    def __init__(self):
        self._fields = set()

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        if not k.startswith('_'):
            self._fields.add(k)
        assert hasattr(self, k)
        assert k in self.__dict__

    def __delattr__(self, k):
        del self.__dict__[k]
        if not k.startswith('_'):
            self._fields.remove(k)
        assert k not in self._fields

    def __iter__(self):
        return iter(self._fields)

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __delitem__(self, key):
        delattr(self, key)

    def __setitem__(self, key, val):
        setattr(self, key, val)

    def __len__(self):
        return len(self._fields)

    def __contains__(self, key):
        return key in self._fields

    @classmethod
    def from_mongo(cls, mongo_document, cache=None):
        """
        Copy the data out of a mongoengine.Document, including nested
        Documents, but do not copy any of the mongo-specific methods or
        attributes.

        Parameters
        ----------
        mongo_document : mongoengine.Document


        cache : dict-like, optional
            Cache of already seen objects in the DB so that we do not
            have to de-reference and build them again.

        """
        if cache is None:
            cache = dict()
        document = Document()
        document._name = mongo_document.__class__.__name__
        fields = set(chain(mongo_document._fields.keys(),
                           mongo_document._data.keys()))

        for field in fields:
            if field == 'id':
                # we are no longer supporting mongo id's making it out of
                # metadatastore
                continue
            attr = getattr(mongo_document, field)
            if isinstance(attr, DBRef):
                oid = attr.id
                try:
                    attr = cache[oid]
                except KeyError:
                    # do de-reference
                    mongo_document.select_related()
                    # grab the attribute again
                    attr = getattr(mongo_document, field)
                    # normalize it
                    attr = _normalize(attr, cache)
                    # and stash for later use
                    cache[oid] = attr
            else:
                attr = _normalize(attr, cache)

            document[field] = attr
        # For debugging, add a human-friendly time_as_datetime attribute.
        if 'time' in document:
            document.time_as_datetime = datetime.fromtimestamp(
                    document.time)
        return document

    @classmethod
    def from_dict(cls, name, input_dict, dref_fields=None, cache=None):
        """Document from dictionary

        Turn a dictionary into a MDS Document, de-referencing
        ObjectId fields as required

        Parameters
        ----------
        name : str
            The class name to assign to the result object

        input_dict : dict
            Raw pymongo document

        dref_fields : dict, optional
            Dictionary keyed on field name mapping to the ReferenceField object
            to use to de-reference the field.

        cache : dict
            Cache dictionary

        Returns
        -------
        doc : Document
            The result as a mds Document
        """
        if cache is None:
            cache = {}
        if dref_fields is None:
            dref_fields = {}

        document = Document()
        document._name = name
        for k, v in six.iteritems(input_dict):
            if k == '_id':
                document['id'] = str(v)
                continue
            if isinstance(v, ObjectId):
                ref_klass = dref_fields[k]
                new_key = ref_klass.name
                try:
                    document[new_key] = cache[v]
                except KeyError:

                    ref_obj = ref_klass.document_type_obj

                    ref_doc = cls.from_mongo(ref_obj.objects.get(id=v))

                    cache[v] = ref_doc
                    document[new_key] = ref_doc
            else:
                document[k] = v
        # For debugging, add a human-friendly time_as_datetime attribute.
        if 'time' in document:
            document.time_as_datetime = datetime.fromtimestamp(
                document.time)
        return document

    def __repr__(self):
        try:
            infostr = '. %s' % self.uid
        except AttributeError:
            infostr = ''
        return "<%s Document%s>" % (self._name, infostr)

    def _str_helper(self, name=None, indent=0):
        """Recursive document walker and formatter

        Parameters
        ----------
        name : str, optional
            Document header name. Defaults to ``self._name``
        indent : int, optional
            The indentation level. Defaults to starting at 0 and adding one tab
            per recursion level
        """
        mapping = {0: '-', 1: '=', 2: '~'}
        ret = "\n%s\n%s" % (name, mapping[indent]*len(name))

        documents = []
        for name, value in sorted(self.items()):
            if isinstance(value, Document):
                documents.append((name, value))
            elif name == 'event_descriptors':
                for val in value:
                    documents.append((name, val))
            elif name == 'data_keys':
                ret += "\n%s" % _prettytable(value).__str__()
            else:
                ret += "\n%-16s: %-40s" % (name[:16], value)
        for name, value in documents:
            ret += "\n%s" % (value._str_helper(value._name, indent+1))
            # ret += "\n"
        ret = ret.split('\n')
        ret = ["%s%s" % ('  '*indent, line) for line in ret]
        ret = "\n".join(ret)
        return ret

    def __str__(self):
        return self._str_helper(self._name)

    def _repr_html_(self):
        return html_table_repr(self)


def _prettytable(data_keys_dict):
    fields = list(data_keys_dict.values())[0]._fields
    table = PrettyTable(["key name"] + list(fields))
    table.align['key name'] = 'l'
    table.padding_width = 1
    for data_key, key_dict in sorted(data_keys_dict.items()):
        row = [data_key]
        for _, v in sorted(key_dict.items()):
            row.append(v)
        table.add_row(row)
    return table


def html_table_repr(obj):
    """Organize nested dict-like and list-like objects into HTML tables."""
    if hasattr(obj, 'items'):
        output = "<table>"
        for key, value in sorted(obj.items()):
            output += "<tr>"
            output += "<td>{key}</td>".format(key=key)
            output += ("<td>" + html_table_repr(value) + "</td>")
            output += "</tr>"
        output += "</table>"
    elif (isinstance(obj, collections.Iterable) and 
          not isinstance(obj, six.string_types)):
        output = "<table style='border: none;'>"
        # Sort list if possible.
        try:
            obj = sorted(obj)
        except TypeError:
            pass
        for value in obj:
            output += "<tr style='border: none;' >"
            output += "<td style='border: none;'>" + html_table_repr(value) 
            output += "</td></tr>"
        output += "</table>"
    elif isinstance(obj, datetime):
        # '1969-12-31 19:00:00' -> '1969-12-31 19:00:00 (45 years ago)'
        human_time = humanize.naturaltime(datetime.now() - obj)
        return str(obj) + '  ({0})'.format(human_time)
    else:
        return str(obj)
    return output
