import pymatrix.constants
import pymatrix.specification.base
import pymatrix.specification.r0.login
import inspect

endpoints = {
    pymatrix.constants.EndpointNamesEnum.Versions:
        "/_matrix/client/versions",
    pymatrix.constants.EndpointNamesEnum.Login:
        "/_matrix/client/r0/login"
    }

class Specification(pymatrix.specification.base.SpecificationBase):

    def _define_message_types(self):
        self.message_code_type = {
            pymatrix.constants.EndpointNamesEnum.Login:
                (pymatrix.specification.r0.login.LoginRequestMessage,
                 pymatrix.specification.r0.login.LoginResponseMessage,
                 pymatrix.specification.base.ErrorMessageBase)
        }
