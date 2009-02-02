import datetime
import simplejson


def date_to_dict(obj):
    return {"year": obj.year, "month": obj.month, "day": obj.day}

def date_from_dict(obj):
    return datetime.date(obj["year"], obj["month"], obj["day"])

def time_to_dict(obj):
    return {"hour": obj.hour, "minute": obj.minute, "second": obj.second,
            "microsecond": obj.microsecond}

def time_from_dict(obj):
    return datetime.time(obj["hour"], obj["minute"], obj["second"], obj["microsecond"])

def datetime_to_dict(obj):
    return {"year": obj.year, "month": obj.month, "day": obj.day, "hour": obj.hour, "minute": obj.minute, "second": obj.second,
            "microsecond": obj.microsecond}

def datetime_from_dict(obj):
    return datetime.datetime(obj["year"], obj["month"], obj["day"], obj["hour"], obj["minute"], obj["second"], obj["microsecond"])


class Encoder(simplejson.JSONEncoder):

    def __init__(self, *a, **k):
        self.obj_to_dict = k.pop("obj_to_dict")
        simplejson.JSONEncoder.__init__(self, *a, **k)

    def default(self, obj):
        name_func = self.obj_to_dict.get(obj.__class__)
        if name_func is None:
            return simplejson.JSONEncoder.default(self, obj)
        (name, func) = name_func
        obj = func(obj)
        obj.update({"__type__": name})
        return obj

class System(object):

    def __init__(self):
        self.obj_to_dict = {}
        self.obj_from_dict = {}

    def register_type(self, cls, obj_to_dict, obj_from_dict, name=None):
        if name is None:
            name == cls.__name__
        self.obj_to_dict[cls] = (name, obj_to_dict)
        self.obj_from_dict[name] = obj_from_dict

    def dumps(self, obj):
        return simplejson.dumps(obj, cls=Encoder, obj_to_dict=self.obj_to_dict)

    def loads(self, s):
        return simplejson.loads(s, object_hook=self._object_hook)

    def _object_hook(self, obj):
        name = obj.get("__type__")
        func = self.obj_from_dict.get(name, None)
        if func is None:
            return obj
        return func(obj)

default_system = System()
default_system.register_type(datetime.date, date_to_dict, date_from_dict, "date")
default_system.register_type(datetime.time, time_to_dict, time_from_dict, "time")
default_system.register_type(datetime.datetime, datetime_to_dict, datetime_from_dict, "datetime")
dumps = default_system.dumps
loads = default_system.loads

decode_mapping = {
    "datetime": datetime_from_dict,
    "date": date_from_dict,
    "time": time_from_dict,
    }

encode_mapping = {
    datetime.datetime: ('datetime',datetime_to_dict),
    datetime.date: ('date',date_to_dict),
    datetime.time: ('time',time_to_dict),
    }

def encode_obj_to_dict(obj, mapping=encode_mapping):
    encode =  mapping.get(type(obj))
    if encode is None:
        return obj
    d = encode[1](obj)
    d['__type__'] = encode[0]
    return d

def decode_obj_from_dict(d, mapping=decode_mapping):
    if not isinstance(d, dict):
        return d
    name = d.get("__type__")
    decode = mapping.get(name, None)
    if decode is None:
        return d
    return decode(d)

def encode_to_dict(obj, mapping=encode_mapping):
    if isinstance(obj, dict):
        return dict( [(k,encode_to_dict(v, mapping)) for k,v in obj.items()] )
    elif isinstance(obj, list):
        return [encode_to_dict(v, mapping) for v in obj]
    else:
        return encode_obj_to_dict(obj, mapping)
    
    
def decode_from_dict(d, mapping=decode_mapping):
    if isinstance(d, dict) and '__type__' not in d:
        return dict( [(k,decode_from_dict(v, mapping)) for k,v in d.items()] )
    elif isinstance(d, list):
        return [decode_from_dict(v, mapping) for v in d]
    else:
        return decode_obj_from_dict(d, mapping)
    
    
