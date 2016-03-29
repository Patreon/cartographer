def filter_dict(dictionary_to_filter):
    return dict((k, v) for k, v in dictionary_to_filter.items() if v is not None)
