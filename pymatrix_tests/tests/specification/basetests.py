from pymatrix_tests.framework.fixture import TestClassBase, testmethod
from pymatrix_tests.framework.asserts import Assert
import pymatrix.error
import pymatrix.specification.base

class SpecificationBaseTests(TestClassBase):

    @testmethod
    @Assert.expectexceptiontype(pymatrix.error.SpecificationError)
    def T_get_message_types_no_types_throw(self):
        # arrange
        class CustomSpec(pymatrix.specification.base.SpecificationBase):
            def _define_message_types(self): pass
        message_code = "abritrary_code"

        # act
        types = CustomSpec().get_message_types(message_code)

    @testmethod
    @Assert.expectexceptiontype(pymatrix.error.SpecificationError)
    def T_get_message_types_with_types_defined_but_not_found_throw(self):
        # arrange
        class MessageType1: pass
        class MessageType2: pass
        class CustomSpec(pymatrix.specification.base.SpecificationBase):
            def _define_message_types(self):
                self.message_code_type = {"type1": MessageType1,
                    "type2": MessageType2}
        message_code = "abritrary_code"

        # act
        types = CustomSpec().get_message_types(message_code)

    @testmethod
    def T_get_message_types_type_code_found_returns_value(self):
        # arrange
        class MessageType1: pass
        class MessageType2: pass
        class CustomSpec(pymatrix.specification.base.SpecificationBase):
            def _define_message_types(self):
                self.message_code_type = {"type1": MessageType1,
                    "type2": MessageType2}
        message_code = "type1"

        # act
        types = CustomSpec().get_message_types(message_code)

        # assert
        assert types == MessageType1

    @testmethod
    def T_get_message_instantiate_first_type_in_tuple(self):
        class MessageType1: pass
        class ResponseType1: pass
        class MessageType2: pass
        class ResponseType2: pass
        class CustomSpec(pymatrix.specification.base.SpecificationBase):
            def _define_message_types(self):
                self.message_code_type = {
                    "type1": (MessageType1, ResponseType1),
                    "type2": (MessageType2, ResponseType2)
                    }
        message_code = "type1"

        # act
        req = CustomSpec().get_message(message_code)

        # assert
        assert isinstance(req, MessageType1)
