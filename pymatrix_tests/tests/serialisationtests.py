from pymatrix_tests.framework.fixture import TestClassBase, testmethod
import pymatrix.serialisation
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

    @testmethod
    def T_serialise_nothing_to_serialise_return_None(self):
        # arrange
        class CustomType:
            int_field = 1
            string_field = "one"

            def method_member(self): pass

        # act
        serialised = pymatrix.serialisation.JsonSerialiser().serialise(CustomType())

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
        serialised = pymatrix.serialisation.JsonSerialiser().serialise(CustomType())

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
        serialised = pymatrix.serialisation.JsonSerialiser().serialise(CustomType())

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
        serialised = pymatrix.serialisation.JsonSerialiser().serialise(CustomType())

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
        serialised = pymatrix.serialisation.JsonSerialiser().serialise(CustomType())

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
        serialised = pymatrix.serialisation.JsonSerialiser().serialise(CustomType())

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
        serialised = pymatrix.serialisation.JsonSerialiser().serialise(CustomType())

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
        serialised = pymatrix.serialisation.JsonSerialiser().serialise(CustomType())

        # assert
        assert serialised == expected_json

    @testmethod
    def T_serialise_very_complex_object_return_expected_json(self):
        # arrange
        class CustomSubSubType:
            @pymatrix.serialisation.serialisable
            def leaf_member(self): return {"key1": "k1"}
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

        expected_json = {"int_field": 1, "string_field": "one",
            "other_field": [
                {"sub_int_member": 456,
                    "collection_strings": ["string 1", "string 2"],
                    "another_complex_member": {"leaf_member": {"key1", "k1"}}},
                {"sub_int_member": 456,
                    "collection_strings": ["string 1", "string 2"],
                    "another_complex_member": {"leaf_member": {"key1", "k1"}}}
            ]}

        # act
        serialised = pymatrix.serialisation.JsonSerialiser().serialise(CustomType())

        # assert
        assert serialised == expected_json
