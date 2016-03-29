from abc import ABCMeta, abstractmethod, abstractproperty


class JSONAPISessionInterface(object):
    _metaclass__ = ABCMeta

    @abstractproperty
    def user_id(self):
        return
