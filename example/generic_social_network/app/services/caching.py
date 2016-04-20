import multiget_cache
from multiget_cache.base_cache_wrapper import cached as library_cached
from multiget_cache.multiget_cache_wrapper import multiget_cached as library_multiget_cached


def get_request_cache():
    return multiget_cache.get_cache()


def clear_request_cache():
    multiget_cache.clear_cache()


def request_cached():
    return library_cached()


def multiget_cached(object_key, argument_key=None, default_result=None,
                    result_fields=None, join_table_name=None):
    # we coerce args to strings so that SQL uses indexes even with mixed-type multiget args lists
    return library_multiget_cached(object_key, argument_key, default_result,
                                   result_fields, join_table_name, coerce_args_to_strings=True)
