from abc import ABCMeta, abstractmethod
import pymatrix.localisation

class RequestMessageBase:
    def __init__(self, type, transport_options=None):
        self._type = type
        self._transport_options = transport_options

    @pymatrix.serialisation.serialisable
    def type(self): return self._type

    @property
    def transport_options(self): return self._transport_options

class ErrorMessageBase:
    def __init__(self, errcode=None, error=None):
        self._errcode = errcode
        self._error = error

    @pymatrix.serialisation.serialisable
    def errcode(self): return self._errcode
    @errcode.setter
    def errcode(self, value): self._errcode = value
    @pymatrix.serialisation.serialisable
    def error(self): return self._error
    @error.setter
    def error(self, value): self._error = value


class SpecificationBase(metaclass=ABCMeta):

    message_code_type = {}

    def __init__(self):
        self._define_message_types()

    @abstractmethod
    def _define_message_types(self): pass

    def get_message_types(self, message_code):
        types_tuple = self.message_code_type.get(message_code, None)
        if(types_tuple is None):
            raise pymatrix.error.SpecificationError(
                pymatrix.localisation.Localisation.get_message(
                    pymatrix.constants.ErrorStringEnum.NotInSpecification
                )
            )
        return types_tuple

    def get_message(self, message_code, **kwargs):
        impl_req_type, impl_resp_type = \
            self.get_message_types(message_code)
        return impl_req_type(**kwargs)
