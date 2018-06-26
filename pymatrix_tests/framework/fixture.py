import inspect
import traceback
from abc import ABCMeta, abstractmethod
from enum import Enum
from pymatrix_tests.framework.time import get_microseconds

### constants
is_test_method = "is_test_method"

class TestStatusEnum(Enum):
    """Lists all known test status"""
    NotRun = "NotRun"
    Pass = "Pass"
    Fail = "Fail"

### functions
def testmethod(func):
    """Decorator for marking test methods. Alias to TestClassBase.testmethod"""
    return TestClassBase.testmethod(func)

def _is_test_method(func):
    return inspect.ismethod(func) and func.__dict__.get(is_test_method, False)

### classes
class TestClassBase(metaclass=ABCMeta):
    def testmethod(func):
        def wrapper(self, func_name, *args, **kwargs):
            start_time = None
            stop_time = None
            try:
                self.test_method_init()
                start_time = get_microseconds()
                func(self, *args, **kwargs)
                stop_time = get_microseconds()
                self.test_method_cleanup()
                return UnitTestResult.complete(func_name, TestStatusEnum.Pass,
                    stop_time-start_time)
            except Exception as e:
                if(stop_time is None):
                    stop_time = get_microseconds()
                return UnitTestResult.complete(func_name, TestStatusEnum.Fail,
                    stop_time-start_time, e)
        wrapper.__dict__[is_test_method] = True
        return wrapper

    def test_method_init(self):
        """Method to initialise fixtures for test methods. Should be
        overridden in a test class for it to do anything."""
        pass

    def test_method_cleanup(self):
        """Method to cleanup after a test method has run. Should be
        overridden in a test class for it to do anything."""
        pass

class UnitTestResult:
    def __init__(self, func_name, status, run_time, exception=None):
        self.func_name = func_name
        self.status = status
        self.run_time = run_time
        self.exception = exception

    def complete(func_name, status, run_time, exception=None):
        if(status == TestStatusEnum.Fail and exception is None):
            raise ValueError("Test is failed but no exception was raised.")
        return UnitTestResult(func_name, status, run_time, exception)

    def __repr__(self):
        exception_repr = self.exception
        if(self.exception is not None):
            exception_repr = traceback.format_exception(self.exception.__class__, self.exception, self.exception.__traceback__)
        return "Func Name: {}; Status: {}; Exception: {}; Run Time: {}".format(self.func_name, self.status, exception_repr, self.run_time)

class TestRunner:
    def run_from_class(self, cls):
        assert inspect.isclass(cls)

        try:
            obj = cls()
        except TypeError as e:
            raise TypeError("cls must be a class instatiable " +
            "without args") from e

        #get all test methods and run them
        test_methods = inspect.getmembers(obj, predicate=_is_test_method)
        return [method[1](method[0]) for method in test_methods]
