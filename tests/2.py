#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import time
from datetime import datetime
from pprint import pprint

from tinydb_jsonorm import Database
from tinydb_jsonorm import TinyJsonModel
from tinydb_jsonorm import fields

from jsonmodels import models

# Hard coded jsonmodels datastores
class CacheType(models.Base):
    __tablename__ = "cachetypes"
    name = fields.StringField(required=True)

# Initialize some default list options
cache_simple = CacheType(name='simple')
cache_memc = CacheType(name='memcached')

def main():
    # Our database
    dbpath = 't1.json'

    # Usando TinyJ
    dbj = Database(dbpath)

    class ConfigModel(TinyJsonModel):
        __tablename__ = "config"

        name = fields.StringField()
        key = fields.StringField()
        CACHE_TYPE = fields.ListField([CacheType])
        last_update = fields.DateTimeField(required=True)
        created_at = fields.DateTimeField(required=True)

        def __init__(self, *args, **kwargs):
            self.last_update = datetime.utcnow()
            self.created_at = self.last_update
            super(ConfigModel, self).__init__(*args, **kwargs)
            
        # this attribute wont be saved because it's not a field
        address = "this attribute will not be saved"

        # Example model custom method
        def created_at_datetime(self):
            return self.created_at

        @property
        def location(self):
            return "Earth"

        class Meta:
            database = dbj

    
    # Create new record
    model = ConfigModel()
    model.name = "original"
    model.key = "test"
    model.CACHE_TYPE = [cache_simple, cache_memc]
    model.created_at = datetime.utcnow()
    model.validate()

    print(model.id, model._cuid)
    # Insert/save the new record
    newrecid = model.insert()
    newreccuid = model._cuid

    # Set table object where perform query, if no set the record is saved in default table of Tinydb
    table = dbj.table(model.__tablename__, cache_size=None)

    # Query all records in table
    allrec = table.all()
    qList = []
    qlist = [ConfigModel(eid=row.eid, **row) for row in allrec]
    print("\nRecords in database: %d" % len(qlist))
    #for rec in qlist:
    #    print("Rec: ", rec.id, rec._cuid, rec.key, rec.name)

    # tinydbj - create model from table's record
    row = table.get(dbj.where("key") == "test")
    new_model = ConfigModel(eid=row.eid, **row)

    print("\nLast inserted record")
    print(new_model.id)
    print(new_model._cuid)
    print(new_model.name)
    print(new_model.key)
    print(new_model.created_at)
    print(new_model.address)
    print(new_model.location)
    print(new_model.created_at_datetime())

    # Change/update record
    print("\nChanging last insert record key field")
    new_model.key = 'dev'
    new_model.save()
    print(new_model.id)
    print(new_model._cuid)
    print(new_model.name)
    print(new_model.key)
    print(new_model.created_at)
    print(new_model.address)
    print(new_model.location)
    print(new_model.created_at_datetime())

    # Create record to be deleted
    delrec = ConfigModel(name="nooriginal", key="tobedeleted", created_at=datetime.utcnow())
    delrecid = delrec.insert()
    delreccuid = delrec._cuid


    # Delete record using table object using id
    print("\nDeleting record: EID==%d, CUID==%s" % (delrecid, delreccuid))
    #rectodel = ConfigModel.get(eid=delrecid)
    #rectodel = ConfigModel.get(dbj.where("key") == "tobedeleted")
    rectodel = ConfigModel.get(cuid=delreccuid)
    print("Created rec: ", model.id, model._cuid, model.key, model.name)
    print("To Delete: ", rectodel.id, rectodel._cuid, rectodel.key, rectodel.name)
    rectodel.delete()

    #drec = ConfigModel(eid=row.eid, **row)
    #print("Rec: ", drec.id, drec.key, drec.name)

if __name__ == "__main__":
    main()

