from abc import ABCMeta, abstractmethod
import inspect

serialisable_label = "serialisable"
def serialisable(func):
    func.__dict__[serialisable_label] = True
    return func

def is_serialisable(method):
    return inspect.ismethod(method) and method.__dict__.get(serialisable_label, False)

def get_serialisables(obj):
    return inspect.getmembers(obj, predicate=is_serialisable)

class SerialiserBase(metaclass=ABCMeta):
    """
    Base serialiser. Describes methods.
    """

    @abstractmethod
    def deserialise(json_data):
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
    def deserialise(json_data):
        pass

    def serialise(self, object):
        return_object = {}
        serialisable_members = get_serialisables(object)
        for member_name, member in serialisable_members:
            value = member()
            if(value is not None):
                return_object[member_name] = value
        return return_object
