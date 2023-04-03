import functools
import traceback
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


def retry_on_exception(number_of_retries: int=3, default_after_all_retries_failed=raise_general_exception(description='All retries exhausted')):
    def retry_func(func):
        l = get_logger()
        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            retries = 0
            while retries < number_of_retries:
                l.info('Try #{} for function {}()'.format(retries, func.__name__))
                try:
                    retries += 1
                    value = func(*args, **kwargs)
                    return Value
                except:
                    l.error('EXCEPTION: {}'.format(traceback.format_exc()))
            l.info('Function {}() retried {} times without success'.format(func.__name__, retries))
            if isinstance(default_after_all_retries_failed, Exception):
                raise default_after_all_retries_failed
            return default_after_all_retries_failed
        return wrapper_func
    return retry_func
