from abc import ABCMeta, abstractmethod
import pymatrix.error
import inspect

class SerialisableProperty(property):
    underlying_type = None

    def __init__(self, fget=None, fset=None, fdel=None, doc=None,
        underlying_type=None):
        self.__setattr__("__doc__", doc)
        self.underlying_type = underlying_type
        super().__init__(fget, fset, fdel, doc)

    def setter(self, fset):
        prop = super().setter(fset)
        prop.underlying_type = self.underlying_type
        prop.__setattr__("__doc__", self.__doc__)
        return prop


def serialisable(arg):
    def make_no_type(func):
        prop = SerialisableProperty(fget=func)
        return prop

    def make_with_type(func):
        prop = SerialisableProperty(fget=func, underlying_type=arg)
        return prop

    if(inspect.isclass(arg)):
        return make_with_type
    return make_no_type(arg)

def is_serialisable(member):
    return isinstance(member, SerialisableProperty)

def get_serialisable_field_metadata(type):
    serialisable_members =  inspect.getmembers(
        type, predicate=is_serialisable
        )
    return dict(serialisable_members)

def get_serialisables(obj):
    serialisable_members =  get_serialisable_field_metadata(obj.__class__)
    return [(name, member.fget(obj)) for name, member
        in serialisable_members.items()]


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

    def _is_primitive(self, obj):
        return isinstance(obj, (int, float, str, bool))
    def _is_collection(self, obj):
        return isinstance(obj, (list, set, tuple))

    def deserialise(self, json_data, type: type):
        if(self._is_primitive(json_data) or json_data is None or type is None):
            return json_data
        if(self._is_collection(json_data)):
            return [self.deserialise(item, type) for item in json_data]

        expected_members = get_serialisable_field_metadata(type)
        obj = type()
        for key, val in json_data.items():
            if(key in expected_members):
                try:
                    obj.__setattr__(key, self.deserialise(val,
                        expected_members[key].underlying_type))
                except AttributeError as ae:
                    raise pymatrix.error.SerialisationError(
                        "There was an error setting the member 'key'.") from ae
            else:
                raise pymatrix.error.SerialisationError(
                    "There is no serialisable member of name 'key'.")
        return obj

    def serialise(self, object):
        if(self._is_primitive(object) or object is None):
            return object

        if(self._is_collection(object)):
            return [self.serialise(sub_item) for sub_item in object]

        if(isinstance(object, dict)):
            return dict([(sub_member_name, self.serialise(sub_value))
                    for sub_member_name, sub_value in object.items()])

        return_object = {}
        serialisable_members = get_serialisables(object)
        for member_name, value in serialisable_members:
            serialised_value = self.serialise(value)
            if(serialised_value is not None):
                return_object[member_name] = serialised_value

        return None if return_object == {} else return_object
