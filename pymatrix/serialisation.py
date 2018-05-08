from abc import ABCMeta, abstractmethod
import inspect

class SerialisableProperty(property):
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)

def serialisable(func):
    prop = SerialisableProperty(fget=func)
    return prop

def is_serialisable(member):
    return isinstance(member, SerialisableProperty)

def get_serialisables(obj):
    serialisable_members =  inspect.getmembers(
        obj.__class__, predicate=is_serialisable
        )
    return [(name, member.fget(obj)) for name, member in serialisable_members]

class SerialiserBase(metaclass=ABCMeta):
    """
    Base serialiser. Describes methods.
    """

    @abstractmethod
    def deserialise(self, json_data, type: type):
        """
        Deserialises a json chuck into an object model
        """
        pass

    @abstractmethod
    def serialise(self, object):
        pass

class JsonSerialiser(SerialiserBase):
    """
    De/serialises the events from/to JSON
    """
    def deserialise(self, json_data, type: type):
        obj = type()
        for key, val in json_data.items():
            obj.__setattr__(key, val)
        return obj

    def serialise(self, object):
        return_object = {}
        serialisable_members = get_serialisables(object)
        for member_name, value in serialisable_members:
            if(value is not None):
                return_object[member_name] = value
        return return_object
