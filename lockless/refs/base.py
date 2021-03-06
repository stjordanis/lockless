import multiprocessing

from .. import version_clock, err

class STMRef(object):
    def __init__(self):
        self.stm_lock = multiprocessing.RLock()
        self.stm_event = multiprocessing.Event()
        self.version = multiprocessing.Value(version_clock.VersionClock.TYPECODE, 0)

    def wait_for_update(self, timeout=None):
        return self.stm_event.wait(timeout=timeout)

    def update(self):
        # this is a bit buggy, since sometimes a transaction will think a
        # value has changed when it hasn't. but this doesn't mess anything up
        # too badly
        self.stm_event.set()
        self.stm_event.clear()

    def _dispatch(self, method_name, *args, **kwargs):
        from .. import core # TODO: only do this once?
        return getattr(core.Transaction.current().get_view_for(self),
                       method_name)(*args, **kwargs)

class STMView(object):
    def __init__(self, txn, stm_ref):
        self.txn = txn
        self.stm_ref = stm_ref
        self.dirty = False

    def _check(self):
        if self.stm_ref.version.value > self.txn.read_version:
            raise err.ConflictError

    def _get_lock_id(self):
        return id(self.stm_ref.stm_lock)

    def _precommit(self):
        if self.dirty:
            self.stm_ref.stm_lock.acquire()
        self._check()

    def _commit(self):
        if self.dirty:
            self.commit()
            self.stm_ref.version.value = version_clock.VersionClock.read()

    def _postcommit(self):
        if self.dirty:
            self.stm_ref.stm_lock.release()
            self.stm_ref.update()

    def commit(self):
        raise NotImplementedError
