import multiprocessing

import base

class STMValue(base.STMVar):
    """ I am the transactional equivalent of a multiprocessing.Value. """
    def __init__(self, *args, **kwargs):
        base.STMVar.__init__(self)
        self._value = multiprocessing.Value(*args, **kwargs)

    def _get_value(self):
        return self._dispatch("_get_value")

    def _set_value(self, value):
        return self._dispatch("_set_value", value)

    value = property(_get_value, _set_value)

class STMValueInstance(base.STMInstance):
    """ only interact with this """
    def __init__(self, txn, stm_value):
        base.STMInstance.__init__(self, txn, stm_value)
        self.temp_value = stm_value._value.value

    def _get_value(self):
        self._check()
        return self.temp_value

    def _set_value(self, value):
        self.dirty = True
        self._check()
        self.temp_value = value

    def commit(self):
        self.stm_var._value.value = self.temp_value
