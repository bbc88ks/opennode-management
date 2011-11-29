from twisted.internet import defer
from zope.component import provideSubscriptionAdapter
from zope.interface import implements

from opennode.oms.model.model.proc import IProcess, Proc, DaemonProcess
from opennode.oms.model.model.compute import ICompute
from opennode.oms.util import subscription_factory, async_sleep
from opennode.oms.zodb import db
from opennode.oms.model.model.symlink import follow_symlinks
from opennode.oms.endpoint.ssh.detached import DetachedProtocol


class SyncDaemonProcess(DaemonProcess):
    implements(IProcess)

    __name__ = "[sync]"

    @defer.inlineCallbacks
    def run(self):
        while True:
            try:
                # Currently we have special codes for gathering info about machines
                # hostinginv VM, in future here we'll traverse the whole zodb and search for gatherers
                # and maintain the gatherers via add/remove events.
                if not self.paused:
                    yield self.sync()
            except Exception:
                import traceback
                traceback.print_exc()
                pass

            yield async_sleep(10)

    @defer.inlineCallbacks
    def sync(self):
        @db.transact
        def get_machines():
            res = []

            oms_root = db.get_root()['oms_root']
            for i in [follow_symlinks(i) for i in oms_root.machines.listcontent()]:
                res.append(i)

            return res

        from opennode.oms.backend.func.compute import SyncAction
        for i in (yield get_machines()):
            if ICompute.providedBy(i):
                print "[sync] syncing", i
                action = SyncAction(i)
                action.execute(DetachedProtocol(), object())

        print "[sync] syncing"

provideSubscriptionAdapter(subscription_factory(SyncDaemonProcess), adapts=(Proc,))
