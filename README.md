# Resilient Code
 
There are three cases of code failures. The first case is known knowns, you can code specifically to detect and handle these cases. The second case is known unknowns, assertions can be used to safeguard against these. The third case is unknown unknowns, where you have to resort to try except, and painfully debug the stack trace each time it occurs.

This library simplifies the way to handle the third case of code failures by introducing decorators and helper functions to automatically handle errors using multiple features such as retrying, logging, dumping variables, all with the minimal amount of code decoration.

[resilient_requests](https://github.com/lohjine/resilient_requests) - Requests-specific resilient code

## Installation

```
pip install git+https://github.com/lohjine/resilient_code
```

## Usage

resilient_code can be used on functions or code blocks.

If used on a function, resilient_code is able to dump local variables. For code blocks, a diff on global variables is done before and after the exception for the variable dump, note that this does not catch variables that are modified within the code block, only newly introduced ones.

By default, resilient will dump variables using `logging`, and re-raise the exception.

You can tweak the number of retries, additionally dump varibles to pickled file, specify variables to dump/ignore. See Args section below.

```python
from resilient_code import resilient, Resilient

# For functions, as a decorator
@resilient
def test():
    raise ValueError
	
# For functions, as an ad-hoc decorator
def test():
    raise ValueError
	
resilient(test)()

# For code blocks
with Resilient():
    raise ValueError
	
# For code blocks, if multiple attempts are required
for attempt in Resilient(max_tries=3):
    with attempt:
        raise ValueError
```

Args: (common for all types)
```
max_tries (int): maximum tries to run function (default=1)
whitelist_var (list of str): list of variables to solely dump in case of exception. If this is populated, blacklist_var is ignored. (default=[])
blacklist_var (list of str): list of variables not to dump in case of exception (default=[])
max_var_str_len (int): maximum length (in terms of string representation) of variable when dumping. This is to avoid dumping an overly huge variable. (default=500)
reraise (bool): whether to raise exception at the end if function always throws exception, or to ignore exception (default=True)
to_log (bool): whether to log error and dump variables to log (default=True)
to_pickle (bool): whether to dump variables to pickled file (default=False)
to_pickle_path (str): filepath to dump variables to pickled file if to_pickle is True (default='exception_variable_dump.pkl')
custom_log_msg (str): message to prepend when logging error (default='')
exponential_backoff (dict):  Backoff parameters for retries. 'min' is number of seconds for the first retry. 'max' is the maximum number of seconds for each retry. Set equal values for both to have a constant retry interval. Note that jitter of 5% is automatically added. (default={'min': 0.1, 'max': 5})
```
