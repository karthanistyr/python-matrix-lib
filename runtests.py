import traceback
from pymatrix_tests.framework.fixture import TestRunner, TestStatusEnum
from pymatrix_tests.tests.serialisationtests import SerialisationTests, \
    SerialisablePropertyTests, JsonSerialiserTests
from pymatrix_tests.tests.specification.basetests import SpecificationBaseTests

classes_to_test = [
    SerialisationTests,
    SerialisablePropertyTests,
    JsonSerialiserTests,
    SpecificationBaseTests
    ]

runner = TestRunner()

results = {}
for testclass in classes_to_test:
    results[testclass] = runner.run_from_class(testclass)

print("Tested {} test classes.".format(len(classes_to_test)))
for result in results:
    nb_passed = 0
    failures = []
    for test in results[result]:
        if(test.status == TestStatusEnum.Pass):
            nb_passed += 1
        if(test.status == TestStatusEnum.Fail):
            failures.append(test)
    print("{}: {} passed, {} failed.".format(result.__name__,
        nb_passed, len(failures)))
    for failure in failures:
        ex_string = traceback.format_exception(failure.exception.__class__,
            failure.exception, failure.exception.__traceback__)
        print("{}: failed with: ""{}""".format(failure.func_name,
            "".join(ex_string)))
