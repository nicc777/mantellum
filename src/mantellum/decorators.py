import functools
import traceback
import time
import random
from mantellum.logging_utils import get_logger
from mantellum.date_and_time_utils import get_utc_timestamp


decorator_logger = get_logger()


def override_logger(new_logger):
    global decorator_logger
    decorator_logger = new_logger


def raise_general_exception(description: str):
    return Exception(description)


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = get_utc_timestamp(with_decimal=True)
        value = func(*args, **kwargs)
        end_time = get_utc_timestamp(with_decimal=True)
        run_time = end_time - start_time
        decorator_logger.info('{}() {} seconds'.format(func.__name__, run_time))
        return value
    return wrapper_timer


def retry_on_exception(
    number_of_retries: int=3,
    default_after_all_retries_failed=None,
    sleep_time_seconds_between_retries: int=1,
    retry_only_named_exceptions: list=list(),
    ignore_retry_on_named_exceptions: list=list(),
    enable_jitter: bool=False
):
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
    remain_in_retry_loop = True
    final_reason = 'All retries failed'
    jitter_time = 0.0
    try:
        def retry_func(func):
            @functools.wraps(func)
            def wrapper_func(*args, **kwargs):
                retries = 0
                while remain_in_retry_loop:
                    decorator_logger.info('Try #{} for function {}()'.format(retries, func.__name__))
                    try:
                        retries += 1
                        value = func(*args, **kwargs)
                        return value
                    except Exception as exception:
                        l.error('EXCEPTION: {}'.format(traceback.format_exc()))
                        exception_name = exception.__class__.__name__

                        do_retry = True
                        if len(retry_only_named_exceptions) > 0:
                            if exception_name not in retry_only_named_exceptions:
                                do_retry = False
                                remain_in_retry_loop = False
                                final_reason = 'Exception named "{}" not found in retry_only_named_exceptions'.format(exception_name)
                        if len(ignore_retry_on_named_exceptions) > 0:
                            if exception_name in ignore_retry_on_named_exceptions:
                                do_retry = False
                                remain_in_retry_loop = False
                                final_reason = 'Exception named "{}" found in ignore_retry_on_named_exceptions'.format(exception_name)

                        if do_retry is True:
                            if enable_jitter is False:
                                time.sleep(sleep_time_seconds_between_retries)
                            else:
                                jitter_time += random.randint(100, 300) / 100.0
                                time.sleep(retries+jitter_time)
                    if number_of_retries > retries:
                        remain_in_retry_loop = False
                decorator_logger.info('Function {}() retried {} times without success'.format(func.__name__, retries-1))
                raise Exception(final_reason)
            return wrapper_func
    except:
        exception_thrown = True
    return retry_func
