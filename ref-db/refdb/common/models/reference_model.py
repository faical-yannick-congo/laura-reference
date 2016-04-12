import datetime
from ..core import db
import json
from bson import ObjectId
          
class ReferenceModel(db.Document):
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    name = db.StringField()
    sizes = db.DictField()
    fit_pressure = db.DictField() # {'aliq1':[], {'aliq2':[]}
    sd_uptake = db.DictField() # {'aliq1':[], {'aliq2':[]}
    av_uptake = db.DictField() # {'aliq1':[], {'aliq2':[]}
    mn_uptake = db.DictField() # {'aliq1':[], {'aliq2':[]}
    md_uptake = db.DictField() # {'aliq1':[], {'aliq2':[]}
    sets = db.DictField(default={}) # Set ids list inclued for this reference.
    possible_status = ["new", "done"]
    status = db.StringField(default="new", choices=possible_status)
    formula = db.DictField(default={})

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def save(self, *args, **kwargs):
        self.created_at = str(datetime.datetime.utcnow())
        return super(ReferenceModel, self).save(*args, **kwargs)

    def summary(self):
        data = {'created-at':self.created_at, 'id':str(self.id),
        'name':self.name, 'sets':self.sets, 'status':self.status}
        return data

    def info(self):
        data = {'created-at':self.created_at, 'id':str(self.id),
        'name':self.name, 'fit-pressure':self.fit_pressure, 'sets':self.sets, 'status':self.status,
        'formula':self.formula,
        'standard-deviation-uptake':self.sd_uptake, 'mean-uptake':self.mn_uptake, 'average-uptake':self.av_uptake,
        'median-uptake':self.md_uptake, 'sizes':self.sizes}
        return data

    def to_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))