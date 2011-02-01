import multiprocessing

import base

class STMArray(base.STMVar):
    """ I am the transactional equivalent of a multiprocessing.Array. """
    def __init__(self, *args, **kwargs):
        base.STMVar.__init__(self)
        self._array = multiprocessing.Array(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self._dispatch("__setitem__", *args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self._dispatch("__getitem__", *args, **kwargs)

    def __setslice__(self, *args, **kwargs):
        return self._dispatch("__setslice__", *args, **kwargs)

    def __getslice__(self, *args, **kwargs):
        return self._dispatch("__getslice__", *args, **kwargs)

class STMArrayInstance(base.STMInstance):
    """ only interact with this """
    def __init__(self, txn, stm_array):
        base.STMInstance.__init__(self, txn, stm_array)
        self.temp_array = stm_array._array.get_obj()._type_ * stm_array._array.get_obj()._length_
        self.temp_array = self.temp_array(*stm_array._array)

    def __setitem__(self, *args, **kwargs):
        self.dirty = True
        self._check()
        return self.temp_array.__setitem__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        self._check()
        return self.temp_array.__getitem__(*args, **kwargs)

    def __setslice__(self, *args, **kwargs):
        self.dirty = True
        self._check()
        return self.temp_array.__setslice__(*args, **kwargs)

    def __getslice__(self, *args, **kwargs):
        self._check()
        return self.temp_array.__getslice__(*args, **kwargs)

    def commit(self):
        self.stm_var._array[:] = self.temp_array
