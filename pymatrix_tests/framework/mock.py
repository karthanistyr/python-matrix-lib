import inspect
from enum import Enum

class MemberNotSetupError(Exception):
    """Should be thrown when a mocked class member was accessed without
    having been setup before, i.e. when the behaviour was not defined."""

    def __init__(self, member_name):
        super().__init__("This member was not setup in strict mode: {}".format(member_name))

def _pass_through_method():
    """Returns a function pointer for a function simply calling pass."""
    def _pass(*args, **kwargs):
        pass
    return _pass

def _return_expression(expression):
    """Returns a function pointer for a function returning the result of an
    arbitrary expression."""

    def _return(*args, **kwargs):
        return expression
    return _return

def _throw_exception(exception: Exception):
    """Returns a function pointer for a function throwing an arbitrary
    exception"""

    def _throw(*args, **kwargs):
        raise exception
    return _throw

def _throw_member_not_setup_exception(member_name):
    """Returns a function pointer to a function throwing the
    MemberNotSetupError exception."""

    return _throw_exception(MemberNotSetupError(member_name))

def _override_property_by_name(obj, property_name, getter):
    if(callable(getattr(obj, property_name))):
        raise ArgumentValidationError("{} is not a field or property name on" +
            " object of type {}".format(property_name, obj.__class__))
    setattr(obj.__class__, property_name,
        property(fget=getter, fset=lambda self, value: value))

def _override_member_by_name(obj, member_name, replacement):
    if(not callable(getattr(obj, member_name))):
        _override_property_by_name(obj, member_name, replacement)
    else:
        setattr(obj, member_name, replacement)

def _override_member_by_name_with_mock(obj, member_name, mock_member):
    mock_member._get_callable_signature(getattr(obj, member_name))
    _override_member_by_name(obj, member_name, mock_member._code)

def _override_all_members_with_throw(obj, excluded_names=None):
    for member_name in obj.__dict__:
        if(excluded_names is None or member_name not in excluded_names):
            _override_member_by_name(obj, member_name,
                _throw_member_not_setup_exception(member_name))

class MockMode(Enum):
    """Mock object members behaviour.
    Loose means that members without an explicit setup will behave identically
    to the members of the same name on the target class.
    Strict means that any member without an explicit setup will throw an
    exception upon being called (this forces the developer to fully
    specify their mock behaviours)."""

    Strict = "Strict"
    Loose = "Loose"

class Mock:
    """Provides an interface for mocking a type and setting up mocked
    member behaviour, i.e. returning something or throwing an exception"""
    def __init__(self, cls, mode: MockMode=MockMode.Strict):
        self.mocked_class = cls
        self.setups = {}
        self.mode = mode

    def setup(self, class_member_name):
        stp = MockedMember(class_member_name)
        self.setups[class_member_name] = stp
        return stp

    def verify(self, class_member_name):
        return self.setups.get(class_member_name, None)

    def object(self):
        proxy_type = type(
            "__{}_Proxy__".format(self.mocked_class.__qualname__),
            (self.mocked_class,),
            {}
            )
        #forcing argument-less ctor
        _override_member_by_name(
            obj=proxy_type,
            member_name="__init__",
            replacement=_pass_through_method())

        mock = proxy_type()
        if(self.mode == MockMode.Strict):
            _override_all_members_with_throw(mock,
                excluded_names={"__init__"}.update(self.setups.keys()))

        for st in self.setups:
            _override_member_by_name_with_mock(mock, st, self.setups[st])

        return mock

class MockedMember:
    """Mock member behaviour. Provides an interface for specifying how a given
    mocked member should behave."""

    def _call_is_legal(self, signature, args, kwargs):
        """Verifies that the arguments respect the signature of the mocked
        function. If the call is legal, return the named arguments' list"""

        call_instance = {}
        if(signature is not None):

            # prepare a list of all positional arguments' arg_names
            # from the signature
            positional_args_in_sig = [param for pkey, param
                in signature.parameters.items()
                if param.default == inspect.Parameter.empty
                    and param.kind != inspect.Parameter.VAR_POSITIONAL]

            # get signature args list, which are ordered
            arg_names = list(signature.parameters.keys())

            if(len(args) > len(arg_names)):
                raise Exception("Too many positional arguments passed.")

            for pos_arg_index in range(0,len(args)):
                call_instance[arg_names[pos_arg_index]] = args[pos_arg_index]

            duplicate_args = [arg_name for arg_name in kwargs
                if arg_name in call_instance]
            if(any(duplicate_args)):
                raise Exception("Mutiple values passed for arguments: {}".format(duplicate_args))

            illegal_args = [arg_name for arg_name in kwargs
                if arg_name not in arg_names]
            if(any(illegal_args)):
                raise Exception("Unknown arguments: {}".format(illegal_args))

            call_instance.update(kwargs)

            missing_args = [pos_arg.name for pos_arg in positional_args_in_sig
                if pos_arg.name not in call_instance]
            if(any(missing_args)):
                raise Exception("Missing positional arguments: {}".format(missing_args))
        return call_instance

    def _track_calls(self, func):
        def track_and_execute(*args, **kwargs):
            self._calls.append(self._call_is_legal(self._signature, args, kwargs))
            return func(*args, **kwargs)

        return track_and_execute

    def __init__(self, cls_member_name):
        self._calls = []
        self._signature = None
        self._code = _throw_member_not_setup_exception(cls_member_name)

    def _get_callable_signature(self, cllble):
        if(callable(cllble)):
            self._signature = inspect.signature(cllble)

    def returns(self, expression):
        self._code = self._track_calls(_return_expression(expression))

    def throws(self, exception: Exception):
        self._code = self._track_calls(_throw_exception(exception))

    def was_called(self, arguments=None, times=None):
        if(arguments is None and times is None):
            return any(self._calls)
        if(arguments is None):
            return len(self._calls) == times
        if(times is None):
            return arguments in self._calls
        return len([args for args in self._calls if args == arguments]) == times
