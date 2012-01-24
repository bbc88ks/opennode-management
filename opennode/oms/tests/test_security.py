import unittest

from nose.tools import eq_, assert_raises
from zope.authentication.interfaces import IAuthentication
from zope.component import getUtility
from zope.security.interfaces import Unauthorized
from zope.securitypolicy.principalpermission import principalPermissionManager as prinperG

from opennode.oms.model.model.base import IContainer
from opennode.oms.model.schema import model_to_dict
from opennode.oms.tests.test_compute import Compute
from opennode.oms.security.checker import proxy_factory
from opennode.oms.security.interaction import OmsSecurityPolicy
from opennode.oms.security.principals import User
from opennode.oms.tests.util import run_in_reactor


class SessionStub(object):

    def __init__(self, principal=None):
        self.principal = principal
        self.interaction = None


class SecurityTestCase(unittest.TestCase):

    def _get_interaction(self, uid):
        auth = getUtility(IAuthentication, context=None)

        interaction = OmsSecurityPolicy()
        sess = SessionStub(auth.getPrincipal(uid))
        interaction.add(sess)
        return interaction

    def make_compute(self, hostname=u'tux-for-test', state=u'active', memory=2000):
        res = Compute(hostname, state, memory)
        res.architecture = 'linux'
        return res

    @run_in_reactor
    def test_test(self):
        auth = getUtility(IAuthentication, context=None)
        auth.registerPrincipal(User('user1'))
        auth.registerPrincipal(User('user2'))

        # setup some fake permissions to the test principals
        prinperG.grantPermissionToPrincipal('read', 'user1')
        prinperG.grantPermissionToPrincipal('zope.Nothing', 'user2')

        # set up interactions
        interaction_user1 = self._get_interaction('user1')
        interaction_user2 = self._get_interaction('user2')

        # get the object being secured
        compute = self.make_compute()
        eq_(compute.architecture, 'linux')

        # get the proxies for the corresponding interactions
        compute_proxy_user1 = proxy_factory(compute, interaction_user1)
        compute_proxy_user2 = proxy_factory(compute, interaction_user2)

        # check an authorized access
        eq_(compute_proxy_user1.architecture, 'linux')

        # check an unauthorized access
        with assert_raises(Unauthorized):
            eq_(compute_proxy_user2.architecture, 'linux')

        # check a default unauthorized access
        with assert_raises(Unauthorized):
            eq_(compute_proxy_user1.state, 'active')

    @run_in_reactor
    def test_adapt(self):
        auth = getUtility(IAuthentication, context=None)
        auth.registerPrincipal(User('user1'))
        interaction = self._get_interaction('user1')

        # get the object being secured
        compute = self.make_compute()
        compute_proxy = proxy_factory(compute, interaction)

        eq_(IContainer(compute), IContainer(compute_proxy))

    @run_in_reactor
    def test_schema(self):
        auth = getUtility(IAuthentication, context=None)
        auth.registerPrincipal(User('user1'))
        interaction = self._get_interaction('user1')

        # get the object being secured
        compute = self.make_compute()
        compute_proxy = proxy_factory(compute, interaction)

        eq_(model_to_dict(compute), model_to_dict(compute_proxy))
        #print model_to_dict(compute)
        #print model_to_dict(compute_proxy)

    def test_with(self):
        interaction = self._get_interaction('user1')

        def dummy():
            yield 2
            with interaction:
                yield 1

        with assert_raises(Exception):
            list(dummy())
