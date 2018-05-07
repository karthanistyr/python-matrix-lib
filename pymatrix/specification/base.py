import pymatrix.serialisation

class TransportOptions:
    options = {}

    def __init__(self, options=None):
        if(options is not None):
            self.options = options

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

    def get_message(self, message_code, **kwargs):
        return self.construct(message_code, **kwargs)

    def construct(self, message_code, **kwargs):
        impl_type = self.message_code_type.get(message_code, None)
        if(impl_type is None):
            raise pymatrix.error.SpecificationError(
                pymatrix.localisation.Localisation.get_message(
                    pymatrix.constants.ErrorStringEnum.NoSuchMessageKnown
                )
            )
        return impl_type(**kwargs)
