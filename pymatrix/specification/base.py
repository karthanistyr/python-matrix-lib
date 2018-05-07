import pymatrix.constants as consts
import pymatrix.error as err
import pymatrix.localisation as loc
import pymatrix.specification.r0 as r0


class _SpecificationVersionBroker:
    def get_spec(self, spec_level: consts.SpecLevelEnum):
        return {
            consts.SpecLevelEnum.r0: r0.Specification()
        }.get(spec_level, None)
        
class MessageBroker:

    _versioned_spec = None

    def __init__(
        self,
        spec_level: consts.SpecLevelEnum,
        spec_broker=_SpecificationVersionBroker()
        ):
        self._spec_level = spec_level
        self._broker = spec_broker
        self._versioned_spec = self._broker.get_spec(self._spec_level)

    def min_spec_level(spec_level: consts.SpecLevelEnum):
        def wrapper(func):
            def run_func(self, *args, **kwargs):
                if(self._spec_level.value >= spec_level.value):
                    return func(self, *args, **kwargs)
                else:
                    raise err.SpecificationError(
                        loc.Localisation.get_message(
                            consts.ErrorStringEnum.NotInSpecification
                        )
                    )
            return run_func
        return wrapper

    @min_spec_level(consts.SpecLevelEnum.r0)
    def get_message(self, message_code, **kwargs):
        return self._versioned_spec.construct(message_code, **kwargs)

    def get_endpoint(self, endpoint_code):
        return self._versioned_spec.endpoints[endpoint_code]
