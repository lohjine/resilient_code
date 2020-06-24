
# we can get at least the input variables

import logging
import pickle
import functools
import time
import random
import traceback
import inspect
import sys
import types


logging.getLogger('resilient_code').addHandler(logging.NullHandler())


def resilient(_func=None, max_tries=1, whitelist_var=[], blacklist_var=[], max_var_str_len=500, to_log=True,
              reraise=True, to_pickle=False, to_pickle_path='exception_variable_dump.pkl', custom_log_msg='',
              exponential_backoff={'min': 0.05, 'max': 1}):
    """
    Decorator for resilient_code

    Args:
        func (function): function to decorate
        max_tries (int): maximum tries to run function
        whitelist_var (list of str): list of variables to solely dump in case of exception. If this is populated, blacklist_var is ignored.
        blacklist_var (list of str): list of variables not to dump in case of exception
        max_var_str_len (int): maximum length (in terms of string representation) of variable when dumping. This is to avoid dumping an overly huge variable.
        reraise (bool): whether to raise exception at the end if function always throws exception, or to ignore exception
        to_log (bool): whether to log error and dump variables to log
        to_pickle (bool): whether to dump variables to pickled file
        to_pickle_path (str): filepath to dump variables to pickled file if to_pickle is True
        custom_log_msg (str): message to prepend when logging error
        exponential_backoff (dict):  Backoff parameters for retries. 'min' is number of seconds for the first retry. 'max' is the maximum number of seconds for each retry. Set equal values for both to have a constant retry interval. Note that jitter of 5% is automatically added.

    Usage:
        1) @resilient
        2) @resilient(max_tries=3, reraise=False)
        3) resilient(example_function, max_tries=3)(arguments)
    """
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_resilient(*args, **kwargs):

            _ = _check_input_arguments(max_tries, whitelist_var, blacklist_var, max_var_str_len, to_log, reraise, to_pickle,
                           to_pickle_path, custom_log_msg, exponential_backoff)

            tries = 0
            sleep_time = -1

            while True:
                tries += 1

                try:
                    r = func(*args, **kwargs)
                except Exception as e:

                    if tries < max_tries:
                        if exponential_backoff:
                            sleep_time = _determine_sleep_time(sleep_time, exponential_backoff['min'],
                                                               exponential_backoff['max'])
                            time.sleep(sleep_time)
                        continue

                    local_var_dump = inspect.trace()[-1][0].f_locals

                    if to_pickle:
                        try:
                            pickle.dump(local_var_dump, open(to_pickle_path, 'wb'))
                        except Exception as e:
                            logging.error(f'Unable to dump pickle file to {to_pickle_path}: {e.with_traceback(None)}')

                    if to_log:
                        msg = f"{' '.join(str(func).split(' ')[:2])+'>'} errored\n    "

                        ## Add custom log message, and traceback if it were to be swallowed afterwards
                        if custom_log_msg:
                            msg += custom_log_msg + '\n    '
                        if not reraise:
                            traceback_msg = traceback.format_exception(*sys.exc_info())
                            msg = msg[:-4] + ''.join(traceback_msg) + '    '

                        ## Log input arguments to function
                        func_arg_msg = ''
                        if args:
                            for idx, i in enumerate(args):
                                if len(str(i)) > max_var_str_len:
                                    if isinstance(i, str):
                                        args[idx] = i[:max_var_str_len]
                                    else:
                                        args[idx] = str(i)[:max_var_str_len]
                            func_arg_msg += f'args: {args}'
                        if kwargs:
                            for i in kwargs:
                                if len(str(kwargs[i])) > max_var_str_len:
                                    if isinstance(kwargs[i], str):
                                        kwargs[i] = kwargs[i][:max_var_str_len]
                                    else:
                                        kwargs[i] = str(kwargs[i])[:max_var_str_len]
                            if args:
                                func_arg_msg += '\n'
                            func_arg_msg += 'kwargs: ' + str(kwargs)
                        if func_arg_msg:
                            msg += func_arg_msg + '\n    '

                        ## Log variable dump
                        for i in local_var_dump:
                            if whitelist_var and i not in whitelist_var:
                                continue
                            if blacklist_var and i in blacklist_var:
                                continue
                            if len(str(local_var_dump[i])) > max_var_str_len: # truncate variables
                                local_var_dump[i] = str(type(local_var_dump[i])) + ' ' + \
                                    str(local_var_dump[i])[:max_var_str_len]

                        msg += f'Exception variable dump: {local_var_dump}'

                        logging.error(msg)

                    if reraise:
                        raise
                    else:
                        return None

            return r

        return wrapper_resilient
    if _func is None:
        return decorator_repeat
    else:
        return decorator_repeat(_func)


class Resilient(object):
    """Code block decorator for resilient_code"""

    def __init__(self, max_tries=1, whitelist_var=[], blacklist_var=[], max_var_str_len=500, to_log=True,
                 reraise=True, _exception_handler=False, exponential_backoff={'min': 0.05, 'max': 1},
                 to_pickle=False, to_pickle_path='exception_variable_dump.pkl', custom_log_msg=''):
        """
        Because there's no function scope, variable dump is done by a diff of variables before the code block and where the exception is raised.
        This will not capture variables that are already defined before the code block and redefined within the code block, and this is intentional for performance reasons.

        Args:
            max_tries (int): maximum tries to run function
            whitelist_var (list of str): list of variables to solely dump in case of exception. If this is populated, blacklist_var is ignored.
            blacklist_var (list of str): list of variables not to dump in case of exception
            max_var_str_len (int): maximum length (in terms of string representation) of variable when dumping. This is to avoid dumping an overly huge variable.
            reraise (bool): whether to raise exception at the end if function always throws exception, or to ignore exception
            to_log (bool): whether to log error and dump variables to log
            to_pickle (bool): whether to dump variables to pickled file
            to_pickle_path (str): filepath to dump variables to pickled file if to_pickle is True
            custom_log_msg (str): message to prepend when logging error
            exponential_backoff (dict):  Backoff parameters for retries. 'min' is number of seconds for the first retry. 'max' is the maximum number of seconds for each retry. Set equal values for both to have a constant retry interval. Note that jitter of 5% is automatically added.

        Usage:
            For max_tries=1 (default)
            ---
            with Resilient():
                # your code

            For max_tries>1
            ---
            for attempt in Resilient(max_tries=2):
                with attempt:
                    # your code
        """
        _ = _check_input_arguments(max_tries, whitelist_var, blacklist_var, max_var_str_len, to_log, reraise, to_pickle,
                           to_pickle_path, custom_log_msg, exponential_backoff)

        self.max_tries = max_tries
        self.tries = 0
        self.whitelist_var = whitelist_var
        self.blacklist_var = blacklist_var
        self.max_var_str_len = max_var_str_len
        self.to_log = to_log
        self.to_pickle = to_pickle
        self.to_pickle_path = to_pickle_path
        self.custom_log_msg = custom_log_msg
        self._exception_handler = _exception_handler
        self.exponential_backoff = exponential_backoff
        self.reraise = reraise
        self.sleep_time = -1

        if not self.whitelist_var and not self._exception_handler and (self.to_log or self.to_pickle):
            self.original_keys = set([i for i in locals().keys() if i[0] != '_'])

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, _traceback,
                 _var_dump=None, exc_info=None):
        global qwe, q, final_keys, yes_keys, ori, no_keys, qwe_processed
        if isinstance(exc_value, BaseException):

            if self._exception_handler:
                # being called by recursive
                if self._exception_handler['last_iter']:
                    self._exception_handler['exception'] = (exc_type, exc_value, _traceback)
                    self._exception_handler['_var_dump'] = inspect.trace()[-1][0].f_locals
                    self._exception_handler['exc_info'] = sys.exc_info()
                    return True
                else:
                    self._exception_handler['exception'] = True
                    return True

            if not _var_dump:
                _var_dump = inspect.trace()[-1][0].f_locals
            if not exc_info:
                exc_info = sys.exc_info()

            if self.whitelist_var:
                final_var_dump = {}
                for i in self.whitelist_var:
                    if i in _var_dump:  # globals():
                        final_var_dump[i] = _var_dump[i]  # globals()[i]
            else:
                # filter out unlikely variables that we would be interested in
                _var_dump = {k: v for k, v in _var_dump.items() if k[0] != '_' and type(v) not in
                             (types.FunctionType, types.ModuleType, types.MethodType, type)}

                final_keys = set(_var_dump.keys()).difference(self.original_keys)

                final_var_dump = {k: _var_dump[k] for k in final_keys}

            if self.to_pickle:
                try:
                    pickle.dump(final_var_dump, open(self.to_pickle_path, 'wb'))
                except Exception as e:
                    logging.error(f'Unable to dump pickle file to {self.to_pickle_path}: {e.with_traceback(None)}')

            if self.to_log:

                msg = f'Code block errored\n    '

                if self.custom_log_msg:
                    msg += self.custom_log_msg + '\n    '

                if not self.reraise:
                    traceback_msg = traceback.format_exception(*exc_info)
                    msg = msg[:-4] + ''.join(traceback_msg) + '    '

                for i in final_var_dump:
                    if self.whitelist_var and i not in self.whitelist_var:
                        continue
                    if self.blacklist_var and i in self.blacklist_var:
                        continue
                    if len(str(final_var_dump[i])) > self.max_var_str_len:  # truncation involves conversion to string
                        final_var_dump[i] = str(type(final_var_dump[i])) + ' ' + \
                            str(final_var_dump[i])[:self.max_var_str_len]

                msg += f'Exception variable dump: {final_var_dump}'

                logging.error(msg)

            if not self.reraise:
                return True  # Swallow exception.

        else:
            # No errors
            pass

    def __iter__(self):
        if self.max_tries == 1:
            raise ValueError("If max_tries == 1, simply do 'with Resilient():' will suffice.")
        _exception_handler = {'last_iter': False, 'exception': None}
        while True:
            self.tries += 1
            yield Resilient(max_tries=1, _exception_handler=_exception_handler)
            if not _exception_handler['exception']:  # no errors
                break
            if self.tries >= self.max_tries:
                # handle error by passing into .__exit__ method
                return self.__exit__(*_exception_handler['exception'], _var_dump=_exception_handler['_var_dump'],
                                     exc_info=_exception_handler['exc_info'])
            elif self.tries + 1 == self.max_tries:
                _exception_handler['last_iter'] = True

            if self.exponential_backoff:
                self.sleep_time = _determine_sleep_time(self.sleep_time, self.exponential_backoff['min'],
                                                        self.exponential_backoff['max'])
                time.sleep(self.sleep_time)


def _determine_sleep_time(current_time, min_time, max_time):
    """Calculates exponential back-off period. Times are in seconds."""
    if current_time == -1:
        current_time = min_time
    else:
        current_time *= 2
        if current_time > max_time:
            current_time = max_time

    # add jitter of 5%
    current_time += random.random() * 0.05 * current_time

    return current_time

def _check_input_arguments(max_tries, whitelist_var, blacklist_var, max_var_str_len, to_log, reraise, to_pickle,
                           to_pickle_path, custom_log_msg, exponential_backoff):
    if not isinstance(max_tries, int):
        raise TypeError(f'max_tries was {max_tries}, but it must be an integer')
    if not max_tries > 0:
        raise ValueError('max_tries must be more than 0')
    if not isinstance(whitelist_var, (list, tuple)):
        raise TypeError(f'whitelist_var was {whitelist_var}, but it must be a list or tuple')
    if not all([isinstance(i, str) for i in whitelist_var]):
        raise ValueError(f'whitelist_var was {whitelist_var}, but it must contain all strings')
    if not isinstance(blacklist_var, (list, tuple)):
        raise TypeError(f'blacklist_var was {blacklist_var}, but it must be a list or tuple')
    if not all([isinstance(i, str) for i in blacklist_var]):
        raise ValueError(f'blacklist_var was {blacklist_var}, but it must contain all strings')
    if not isinstance(max_var_str_len, int):
        raise TypeError(f'max_var_str_len was {max_var_str_len}, but it must be an integer')
    if not max_var_str_len >= 0:
        raise ValueError('max_var_str_len must be more than or equal to 0')
    if not isinstance(to_log, bool):
        raise TypeError(f'to_log was {to_log}, but it must be a boolean')
    if not isinstance(reraise, bool):
        raise TypeError(f'reraise was {reraise}, but it must be a boolean')
    if not isinstance(to_pickle, bool):
        raise TypeError(f'to_pickle was {to_pickle}, but it must be a boolean')
    if not isinstance(to_pickle_path, str):
        raise TypeError(f'to_pickle was {to_pickle_path}, but it must be a string')
    if not isinstance(custom_log_msg, str):
        raise TypeError(f'to_pickle was {custom_log_msg}, but it must be a string')
    if not (isinstance(exponential_backoff, dict) or not exponential_backoff):
        raise TypeError(f'exponential_backoff was {exponential_backoff}, but it must be a dict or falsy')
    if isinstance(exponential_backoff, dict):
        if not (isinstance(exponential_backoff.get('min', False), (float, int)) and isinstance(exponential_backoff.get('max', False), (float, int))):
            raise ValueError(f"exponential_backoff was {exponential_backoff}, but it must contain keys 'min' and 'max' with float/int values")
    return True