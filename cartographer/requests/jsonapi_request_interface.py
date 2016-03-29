from abc import ABCMeta, abstractmethod


class JSONAPIRequestInterface(object):
    _metaclass__ = ABCMeta

    @abstractmethod
    def get_json_api_version(self):
        return

    @abstractmethod
    def get_json(self, force=False):
        return

    @abstractmethod
    def get_includes(self):
        return

    @abstractmethod
    def get_requested_fields(self):
        return
