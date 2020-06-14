from unittest import TestCase
from resilient_code import resilient, Resilient
import types

def function_raise_exception():
    new_var = 1
    raise ValueError('error')
    return new_var

@resilient
def function_raise_exception_decorated(awd):
    new_var = 2
    raise ValueError
    return new_var

function_raise_exception_decorated(awd=3)

@resilient(max_tries=1, custom_log_msg='custom log message test')
def function_raise_exception_decorated_custom_args():
    new_var = 3
    raise ValueError
    return new_var

for attempt in Resilient(max_tries=2):
    with attempt:
        print(0)
        raise ValueError
        
        
import sys
import traceback
import inspect
try:
    1
    raise ValueError('error')
except Exception as e:
    q = e
    w =sys.exc_info()
    
    r= traceback.format_exception(*sys.exc_info())



with Resilient():
    new_var = 5
    raise ValueError


_local = set(locals().keys())
_globa = set(globals().keys())


try:
    asd = 5
    _r_local = set([i for i in locals().keys() if i[0]!='_'])
    raise ValueError
    sdf = 6
except:
    _var_dump = inspect.trace()[-1][0].f_locals
    _var_dump = {k: v for k, v in _var_dump.items() if k[0] != '_' and type(v) not in (types.FunctionType, types.ModuleType, type)}
    _f_local = set([i for i in _var_dump.keys() if i[0]!='_' and type(i)])
    
    _n_local = set([i for i in locals().keys() if i[0]!='_'])
    
    _wtff_local = set([i for i in _var_dump.keys() if i[0]!='_'])
    
_r_local.difference(_local)
_f_local.difference(_local)
_n_local.difference(_local)
_wtff_local.difference(_local)
    


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