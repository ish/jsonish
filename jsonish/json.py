import simplejson


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


class JSON(object):

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


json = JSON()
dumps = json.dumps
loads = json.loads

