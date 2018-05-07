import pymatrix.api
import pymatrix.backend.http
import pymatrix.serialisation

DEFAULT_BACKEND_TYPE = pymatrix.backend.http.HttpBackend
DEFAULT_SERIALISER_TYPE = pymatrix.serialisation.JsonSerialiser
DEFAULT_API_TYPE = pymatrix.api.RestApi

def get_instance(type: type):
    try:
        return type()
    except:
        raise
