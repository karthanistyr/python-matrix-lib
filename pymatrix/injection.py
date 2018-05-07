import pymatrix.api
import pymatrix.backend.http
import pymatrix.serialisation
import pymatrix.specification.r0

DEFAULT_BACKEND_TYPE = pymatrix.backend.http.HttpBackend
DEFAULT_SERIALISER_TYPE = pymatrix.serialisation.JsonSerialiser
DEFAULT_API_TYPE = pymatrix.api.RestApi

SPEC_R0 = pymatrix.specification.r0.Specification

def get_instance(type: type):
    return type()
