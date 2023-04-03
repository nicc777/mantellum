import functools

from mantellum.logging_utils import get_logger
from mantellum.date_and_time_utils import get_utc_timestamp


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
