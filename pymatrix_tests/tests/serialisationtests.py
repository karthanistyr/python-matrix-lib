from pymatrix_tests.framework.fixture import TestClassBase, testmethod
from pymatrix_tests.framework.asserts import Assert
import pymatrix.serialisation
import pymatrix.error
import inspect

def get_member_by_name(obj, name):
    eligible_members = [member[1] for member in inspect.getmembers(obj)\
        if member[0] == name]

    if(len(eligible_members) == 1):
        return eligible_members[0]


class SerialisationTests(TestClassBase):

    @testmethod
    def T_serialisable_no_type_returns_SerialisableProperty(self):
        # arrange
        def int_member(self): return 123

        # act
        prop = pymatrix.serialisation.serialisable(int_member)

        # assert
        assert isinstance(prop, pymatrix.serialisation.SerialisableProperty)

    @testmethod
    def T_serialisable_no_type_sets_no_underlying_type(self):
        # arrange
        def int_member(self): return 123

        # act
        prop = pymatrix.serialisation.serialisable(int_member)

        # assert
        assert prop.underlying_type is None

    @testmethod
    def T_serialisable_with_type_returns_SerialisableProperty(self):
        # arrange
        class CustomType: pass
        def int_member(self): return 123

        # act
        prop = pymatrix.serialisation.serialisable(CustomType)(int_member)

        # assert
        assert isinstance(prop, pymatrix.serialisation.SerialisableProperty)

    @testmethod
    def T_serialisable_with_type_sets_underlying_type(self):
        # arrange
        class CustomType: pass
        def int_member(self): return 123

        # act
        prop = pymatrix.serialisation.serialisable(CustomType)(int_member)

        # assert²
        assert prop.underlying_type is not None
        assert prop.underlying_type == CustomType

    @testmethod
    def T_serialisable_decorator_no_type_makes_SerialisableProperty(self):
        # arrange
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_member(self): return 123

        # assert
        member = get_member_by_name(CustomType, "int_member")
        assert isinstance(member, pymatrix.serialisation.SerialisableProperty)
        assert member.underlying_type is None

    @testmethod
    def T_serialisable_decorator_with_type_makes_SerialisableProperty(self):
        # arrange
        class CustomSubType: pass
        class CustomType:
            @pymatrix.serialisation.serialisable(CustomSubType)
            def int_member(self): return 123
            @int_member.setter
            def int_member(self, value): self._int_member = value

        # assert
        member = get_member_by_name(CustomType, "int_member")
        assert isinstance(member, pymatrix.serialisation.SerialisableProperty)
        assert member.underlying_type == CustomSubType

    @testmethod
    def T_get_serialisables_no_serialisable_member_return_empty_list(self):
        # arrange
        class CustomType: pass

        # act
        serialisables = pymatrix.serialisation.get_serialisables(CustomType())

        # assert
        assert not any(serialisables)

    @testmethod
    def T_get_serialisables_with_serialisable_member_return_list(self):
        # arrange
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_member(self): return 123
            # not serialised
            @property
            def string_member(self): return "string"

        # act
        serialisables = pymatrix.serialisation.get_serialisables(CustomType())

        # assert
        assert any(serialisables)
        assert len(serialisables) == 1
        member_name, member_value = serialisables[0]
        assert member_name == "int_member"
        assert member_value == 123

    @testmethod
    def T_is_serialisable_if_SerialisableProperty_return_true(self):
        # arrange
        obj = pymatrix.serialisation.SerialisableProperty()

        # act
        result = pymatrix.serialisation.is_serialisable(obj)

        # assert
        assert result # must be true


    @testmethod
    def T_is_serialisable_if_not_SerialisableProperty_return_false(self):
        # arrange
        class CustomProperty: pass
        obj = CustomProperty()

        # act
        result = pymatrix.serialisation.is_serialisable(obj)

        # assert
        assert not result

class SerialisablePropertyTests(TestClassBase):

    @testmethod
    def T_ctor_arguments_end_up_in_correct_places_positional(self):
        # arrange
        def my_getter(self): pass
        def my_setter(self, value): pass
        def my_deleter(self): pass
        my_doc = "A docstring here"
        class my_underlying_type: pass

        # act
        prop = pymatrix.serialisation.SerialisableProperty(
            my_getter, my_setter, my_deleter, my_doc, my_underlying_type)

        # assert
        assert prop.fget == my_getter
        assert prop.fset == my_setter
        assert prop.fdel == my_deleter
        assert prop.__doc__ == my_doc
        assert prop.underlying_type == my_underlying_type

class JsonSerialiserTests(TestClassBase):

    def test_method_init(self):
        self._serialiser = pymatrix.serialisation.JsonSerialiser()

    @testmethod
    def T_serialise_nothing_to_serialise_return_None(self):
        # arrange
        class CustomType:
            int_field = 1
            string_field = "one"

            def method_member(self): pass

        # act
        serialised = self._serialiser.serialise(CustomType())

        # assert
        assert serialised is None

    @testmethod
    def T_serialise_flat_object_return_flat_json(self):
        # arrange
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_field(self): return 1
            @pymatrix.serialisation.serialisable
            def string_field(self): return "one"
        expected_json = {"int_field": 1, "string_field": "one"}


        # act
        serialised = self._serialiser.serialise(CustomType())

        # assert
        assert serialised == expected_json

    @testmethod
    def T_serialise_flat_object_ignore_non_serialised_return_flat_json(self):
        # arrange
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_field(self): return 1
            @pymatrix.serialisation.serialisable
            def string_field(self): return "one"
            @property # this is not serialisable
            def other_field(self): return "other"
        expected_json = {"int_field": 1, "string_field": "one"}


        # act
        serialised = self._serialiser.serialise(CustomType())

        # assert
        assert serialised == expected_json

    @testmethod
    def T_serialise_flat_object_ignore_null_members_return_flat_json(self):
        # arrange
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_field(self): return 1
            @pymatrix.serialisation.serialisable
            def string_field(self): return None
        expected_json = {"int_field": 1}


        # act
        serialised = self._serialiser.serialise(CustomType())

        # assert
        assert serialised == expected_json

    @testmethod
    def T_serialise_complex_object_return_complex_json(self):
        # arrange
        class CustomSubType:
            @pymatrix.serialisation.serialisable
            def sub_int_member(self): return 456
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_field(self): return 1
            @pymatrix.serialisation.serialisable
            def string_field(self): return "one"
            @pymatrix.serialisation.serialisable
            def other_field(self): return CustomSubType()

        expected_json = {"int_field": 1, "string_field": "one",
            "other_field": {"sub_int_member": 456}}

        # act
        serialised = self._serialiser.serialise(CustomType())

        # assert
        assert serialised == expected_json

    @testmethod
    def T_serialise_complex_object_no_serable_sub_member_treat_as_null(self):
        """
        Serialises a structure but the complex object member
        has no serialisable member itself
        """
        # arrange
        class CustomSubType:
            @property # not serialisable
            def sub_int_member(self): return 456
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_field(self): return 1
            @pymatrix.serialisation.serialisable
            def string_field(self): return "one"
            @pymatrix.serialisation.serialisable
            def other_field(self): return CustomSubType()

        expected_json = {"int_field": 1, "string_field": "one"}

        # act
        serialised = self._serialiser.serialise(CustomType())

        # assert
        assert serialised == expected_json

    @testmethod
    def T_serialise_complex_object_only_null_sub_member_treat_as_null(self):
        """
        Serialises a structure, the complex object member has
        serialisable members itself, but none of them have a value
        """
        # arrange
        class CustomSubType:
            @pymatrix.serialisation.serialisable
            def sub_int_member(self): return None
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_field(self): return 1
            @pymatrix.serialisation.serialisable
            def string_field(self): return "one"
            @pymatrix.serialisation.serialisable
            def other_field(self): return CustomSubType()

        expected_json = {"int_field": 1, "string_field": "one"}

        # act
        serialised = self._serialiser.serialise(CustomType())

        # assert
        assert serialised == expected_json

    @testmethod
    def T_serialise_complex_object_repr_collection_return_array_json(self):
        # arrange
        class CustomSubType:
            @pymatrix.serialisation.serialisable
            def sub_int_member(self): return 456
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_field(self): return 1
            @pymatrix.serialisation.serialisable
            def string_field(self): return "one"
            @pymatrix.serialisation.serialisable
            def other_field(self): return [CustomSubType(), CustomSubType()]

        expected_json = {"int_field": 1, "string_field": "one",
            "other_field": [{"sub_int_member": 456},{"sub_int_member": 456}]}

        # act
        serialised = self._serialiser.serialise(CustomType())

        # assert
        assert serialised == expected_json

    @testmethod
    def T_serialise_very_complex_object_return_expected_json(self):
        # arrange
        class CustomEndType:
            @pymatrix.serialisation.serialisable
            def this_member(self): return 0
        class CustomSubSubType:
            @pymatrix.serialisation.serialisable
            def leaf_member(self): return {"key1": "k1"}
            @pymatrix.serialisation.serialisable
            def other_leaf_member(self): return {"key2": CustomEndType()}
        class CustomSubType:
            @pymatrix.serialisation.serialisable
            def sub_int_member(self): return 456
            @pymatrix.serialisation.serialisable
            def collection_strings(self): return ["string 1", "string 2"]
            @pymatrix.serialisation.serialisable
            def another_complex_member(self): return CustomSubSubType()
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_field(self): return 1
            @pymatrix.serialisation.serialisable
            def string_field(self): return "one"
            @pymatrix.serialisation.serialisable
            def other_field(self): return [CustomSubType(), CustomSubType()]

        expected_json = {"int_field": 1,
            "other_field": [
                {"another_complex_member": {
                        "leaf_member": {"key1": "k1"},
                        "other_leaf_member": {"key2": {"this_member": 0}}},
                    "collection_strings": ["string 1", "string 2"],
                    "sub_int_member": 456},
                {"another_complex_member": {
                        "leaf_member": {"key1": "k1"},
                        "other_leaf_member": {"key2": {"this_member": 0}}},
                    "collection_strings": ["string 1", "string 2"],
                    "sub_int_member": 456}
            ],
            "string_field": "one"}

        # act
        serialised = self._serialiser.serialise(CustomType())

        # assert
        assert serialised == expected_json

    @testmethod
    def T_deserialise_flat_json_into_flat_object(self):
        # arrange
        flat_json = {"member_one": 1, "member_two": "two"}
        class FlatType:
            @pymatrix.serialisation.serialisable
            def member_one(self): return self._member_one
            @member_one.setter
            def member_one(self, value): self._member_one = value
            @pymatrix.serialisation.serialisable
            def member_two(self): return self._member_two
            @member_two.setter
            def member_two(self, value): self._member_two = value

        # act
        obj = self._serialiser.deserialise(flat_json, FlatType)

        # assert
        assert isinstance(obj, FlatType)
        assert obj.member_one == 1
        assert obj.member_two == "two"

    @testmethod
    @Assert.expectexceptiontype(pymatrix.error.SerialisationError)
    def T_deserialise_flat_json_target_type_missing_member_throw(self):
        # arrange
        flat_json = {"member_one": 1, "member_two": "two"}
        class FlatType:
            @pymatrix.serialisation.serialisable
            def member_one(self): return self._member_one
            @member_one.setter
            def member_one(self, value): self._member_one = value

        # act
        obj = self._serialiser.deserialise(flat_json, FlatType)

    @testmethod
    @Assert.expectexceptiontype(pymatrix.error.SerialisationError)
    def T_deserialise_flat_json_target_type_non_serable_member_throw(self):
        # arrange
        flat_json = {"member_one": 1, "member_two": "two"}
        class FlatType:
            @pymatrix.serialisation.serialisable
            def member_one(self): return self._member_one
            @member_one.setter
            def member_one(self, value): self._member_one = value
            @property
            def member_two(self): return self._member_two
            @member_two.setter
            def member_two(self, value): self._member_two = value

        # act
        obj = self._serialiser.deserialise(flat_json, FlatType)

    @testmethod
    @Assert.expectexceptiontype(pymatrix.error.SerialisationError)
    def T_deserialise_flat_json_target_type_readonly_member_throw(self):
        # arrange
        flat_json = {"member_one": 1, "member_two": "two"}
        class FlatType:
            @pymatrix.serialisation.serialisable
            def member_one(self): return self._member_one
            @member_one.setter
            def member_one(self, value): self._member_one = value
            @pymatrix.serialisation.serialisable
            def member_two(self): return self._member_two

        # act
        obj = self._serialiser.deserialise(flat_json, FlatType)

    @testmethod
    def T_deserialise_complex_json_return_complex_object(self):
        # arrange
        complex_json = {"member_one": 1, "member_two": {"sub_member": "abc"}}
        class SubType:
            @pymatrix.serialisation.serialisable
            def sub_member(self): return self._sub_member
            @sub_member.setter
            def sub_member(self, value): self._sub_member = value
        class ComplexType:
            @pymatrix.serialisation.serialisable
            def member_one(self): return self._member_one
            @member_one.setter
            def member_one(self, value): self._member_one = value
            @pymatrix.serialisation.serialisable(SubType)
            def member_two(self): return self._member_two
            @member_two.setter
            def member_two(self, value): self._member_two = value

        # act
        obj = self._serialiser.deserialise(complex_json, ComplexType)

        # assert
        assert isinstance(obj, ComplexType)
        assert obj.member_one == 1
        assert isinstance(obj.member_two, SubType)
        assert obj.member_two.sub_member == "abc"

    @testmethod
    def T_deserialise_json_array_into_list(self):
        # arrange
        json_array = { "my_array": [
            {"int_member": 1},
            {"int_member": 2},
            {"int_member": 3},
            {"int_member": 4}
        ]}
        class SubType:
            @pymatrix.serialisation.serialisable
            def int_member(self): return self._int_member
            @int_member.setter
            def int_member(self, value): self._int_member = value
        class ObjectType:
            @pymatrix.serialisation.serialisable(SubType)
            def my_array(self): return self._my_array
            @my_array.setter
            def my_array(self, value): self._my_array = value

        # act
        obj = self._serialiser.deserialise(json_array, ObjectType)

        # assert
        assert isinstance(obj, ObjectType)
        assert isinstance(obj.my_array, list)
        assert len(obj.my_array) == 4

        first_value = 1
        for sub in obj.my_array:
            assert sub.int_member == first_value
            first_value += 1

    @testmethod
    def T_deserialise_unspecified_dict_stored_as_is(self):
        # arrange
        sub_dict = { "arbitrary": 1, "other": "test"}
        json_with_dict = {"my_dictionary": sub_dict}
        class ObjectType:
            @pymatrix.serialisation.serialisable
            def my_dictionary(self): return self._my_dictionary
            @my_dictionary.setter
            def my_dictionary(self, value): self._my_dictionary = value

        # act
        obj = self._serialiser.deserialise(json_with_dict, ObjectType)

        # assert
        assert isinstance(obj, ObjectType)
        assert obj.my_dictionary == sub_dict

    @testmethod
    def T_deserialise_json_primitive_returns_primitive(self):
        # arrange
        json_primitive = { "my_primitive": 1 }
        class ObjectType:
            @pymatrix.serialisation.serialisable
            def my_primitive(self): return self._my_primitive
            @my_primitive.setter
            def my_primitive(self, value): self._my_primitive = value

        # act
        obj = self._serialiser.deserialise(json_primitive, ObjectType)

        # assert
        assert isinstance(obj, ObjectType)
        assert obj.my_primitive == 1

    @testmethod
    def T_deserialise_very_complex_json_returns_complex_obj_structure(self):
        # arrange
        very_complex_json = {"int_field": 1,
            "other_field": [
                {"another_complex_member": {
                        "leaf_member": {"key1": "k1"},
                        "other_leaf_member": {"this_member": 0}},
                    "collection_strings": ["string 1", "string 2"],
                    "sub_int_member": 456},
                {"another_complex_member": {
                        "leaf_member": {"key1": "k1"},
                        "other_leaf_member": {"this_member": 0}},
                    "collection_strings": ["string 1", "string 2"],
                    "sub_int_member": 456}
            ],
            "string_field": "one"}
        class CustomEndType:
            @pymatrix.serialisation.serialisable
            def this_member(self): return self._this_member
            @this_member.setter
            def this_member(self, value): self._this_member = value
        class CustomSubSubType:
            @pymatrix.serialisation.serialisable
            def leaf_member(self): return self._leaf_member
            @leaf_member.setter
            def leaf_member(self, value): self._leaf_member = value
            @pymatrix.serialisation.serialisable(CustomEndType)
            def other_leaf_member(self):
                return self._other_leaf_member
            @other_leaf_member.setter
            def other_leaf_member(self, value):
                self._other_leaf_member = value
        class CustomSubType:
            @pymatrix.serialisation.serialisable
            def sub_int_member(self): return self._sub_int_member
            @sub_int_member.setter
            def sub_int_member(self, value): self._sub_int_member = value
            @pymatrix.serialisation.serialisable
            def collection_strings(self): return self._collection_strings
            @collection_strings.setter
            def collection_strings(self, value): self._collection_strings=value
            @pymatrix.serialisation.serialisable(CustomSubSubType)
            def another_complex_member(self):
                return self._another_complex_member
            @another_complex_member.setter
            def another_complex_member(self, value):
                self._another_complex_member = value
        class CustomType:
            @pymatrix.serialisation.serialisable
            def int_field(self): return self._int_field
            @int_field.setter
            def int_field(self, value): self._int_field = value
            @pymatrix.serialisation.serialisable
            def string_field(self): return self._string_field
            @string_field.setter
            def string_field(self, value): self._string_field = value
            @pymatrix.serialisation.serialisable(CustomSubType)
            def other_field(self): return self._other_field
            @other_field.setter
            def other_field(self, value): self._other_field = value

        # act
        obj = self._serialiser.deserialise(very_complex_json, CustomType)

        # assert
        assert isinstance(obj, CustomType)
        assert obj.int_field == 1
        assert obj.string_field == "one"
        assert isinstance(obj.other_field, list)
        for other_field in obj.other_field:
            assert other_field.sub_int_member == 456
            assert isinstance(other_field.collection_strings, list)
            assert other_field.collection_strings == ["string 1", "string 2"]
            assert isinstance(other_field.another_complex_member,
                CustomSubSubType)
            assert other_field.another_complex_member.leaf_member \
                == {"key1": "k1"}
            assert isinstance(other_field.another_complex_member\
                .other_leaf_member, CustomEndType)
            assert other_field.another_complex_member.other_leaf_member\
                .this_member == 0
