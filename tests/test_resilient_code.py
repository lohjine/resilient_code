from unittest import TestCase
from resilient_code import resilient, Resilient

def function_raise_exception():
    new_var = 1
    raise ValueError('error')
    return new_var

@resilient
def function_raise_exception_decorated(awd):
    new_var = 2
    raise ValueError
    return new_var

@resilient(reraise=False)
def function_raise_exception_decorated_withoutreraise(awd):
    new_var = 2
    raise ValueError
    return new_var


@resilient(max_tries=1, custom_log_msg='custom log message test')
def function_raise_exception_decorated_custom_args():
    new_var = 3
    raise ValueError
    return new_var

for attempt in Resilient(max_tries=2, reraise=False):
    with attempt:
        print(0)
        raise ValueError


class TestGet(TestCase):
    def test_decorated_function(self):
        try:
            function_raise_exception_decorated()
            self.assertTrue(False)
        except:
            self.assertTrue(True)

    def test_decorated_function_custom_args(self):
        try:
            function_raise_exception_decorated_custom_args()
            self.assertTrue(False)
        except:
            self.assertTrue(True)

    def test_adhoc_decorated_function(self):
        try:
            resilient(function_raise_exception)()
            self.assertTrue(False)
        except:
            self.assertTrue(True)

    def test_adhoc_decorated_function_reraisefalse(self):
        try:
            resilient(function_raise_exception, reraise=False)()
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_code_block(self):
        try:
            with Resilient():
                new_var = 5
                raise ValueError
                return new_var
            self.assertTrue(False)
        except:
            self.assertTrue(True)

    def test_code_block_reraisefalse(self):
        try:
            with Resilient(reraise=False):
                new_var = 5
                raise ValueError
                return new_var
            self.assertTrue(True)
        except:
            self.assertTrue(False)