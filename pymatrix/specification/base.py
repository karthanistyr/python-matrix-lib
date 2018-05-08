import pymatrix.serialisation

class RequestMessageBase:
    def __init__(self, type, transport_options=None):
        self._type = type
        self._transport_options = transport_options

    @pymatrix.serialisation.serialisable
    def type(self):
        return self._type

    @property
    def transport_options(self):
        return self._transport_options

class SpecificationBase:

    def get_message_types(self, message_code):
        types_tuple = self.message_code_type.get(message_code, None)
        if(types_tuple is None):
            pymatrix.error.SpecificationError(
                pymatrix.localisation.Localisation.get_message(
                    pymatrix.constants.ErrorStringEnum.NoSuchMessageKnown
                )
            )
        return types_tuple
        
    def get_message(self, message_code, **kwargs):
        impl_req_type, impl_resp_type = \
            self.message_code_type.get(message_code, None)
        if(impl_req_type is None):
            raise pymatrix.error.SpecificationError(
                pymatrix.localisation.Localisation.get_message(
                    pymatrix.constants.ErrorStringEnum.NoSuchMessageKnown
                )
            )
        return impl_req_type(**kwargs)
