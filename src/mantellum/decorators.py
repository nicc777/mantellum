import functools
import traceback
import time
from mantellum.logging_utils import get_logger
from mantellum.date_and_time_utils import get_utc_timestamp


def raise_general_exception(description: str):
    return Exception(description)


def timer(func):
    l = get_logger()
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = get_utc_timestamp(with_decimal=True)
        value = func(*args, **kwargs)
        end_time = get_utc_timestamp(with_decimal=True)
        run_time = end_time - start_time
        l.info('Function {}() finished in {} seconds'.format(func.__name__, run_time))
        return value
    return wrapper_timer


def retry_on_exception(number_of_retries: int=3, default_after_all_retries_failed=None, sleep_time_seconds_between_retries: int=1):
    """
    Example usage (Forcing a failure):

        >>> from mantellum.decorators import *
        >>> @retry_on_exception(number_of_retries=4, default_after_all_retries_failed='It Failed!')
        ... def F():
        ...     raise Exception('This will never work!')
        ... 
        >>> F()
        'It Failed!'
        >>> 

    Example usage (Normal usage with defaults):
        >>> from mantellum.decorators import *
        >>> @retry_on_exception()
        ... def F():
        ...     return 123
        ... 
        >>> F()
        123
    """
    exception_thrown = False
    try:
        def retry_func(func):
            l = get_logger()
            @functools.wraps(func)
            def wrapper_func(*args, **kwargs):
                retries = 0
                while retries < number_of_retries+1:
                    l.info('Try #{} for function {}()'.format(retries, func.__name__))
                    try:
                        retries += 1
                        value = func(*args, **kwargs)
                        return value
                    except:
                        l.error('EXCEPTION: {}'.format(traceback.format_exc()))
                        time.sleep(sleep_time_seconds_between_retries)
                l.info('Function {}() retried {} times without success'.format(func.__name__, retries-1))
                raise Exception('All retries failed')
            return wrapper_func
    except:
        exception_thrown = True
    return retry_func
