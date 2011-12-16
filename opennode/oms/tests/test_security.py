import unittest

from nose.tools import eq_, assert_raises
from zope.authentication.interfaces import IAuthentication, PrincipalLookupError
from zope.component import provideUtility, getUtility
from zope.interface import implements
from zope.security.interfaces import Unauthorized, ForbiddenAttribute
from zope.securitypolicy.principalpermission import principalPermissionManager as prinperG
from zope.securitypolicy.zopepolicy import ZopeSecurityPolicy

from opennode.oms.model.model.compute import Compute
from opennode.oms.security.checker import proxy_factory
from opennode.oms.security.principals import User
from opennode.oms.tests.util import run_in_reactor


class SessionStub(object):

    def __init__(self, principal=None):
        self.principal = principal
        self.interaction = None


class DummyAuthenticationUtility:
    implements(IAuthentication)

    def getPrincipal(self, id):
         if id == 'user1':
             return User(id)
         elif id == 'user2':
             return User(id)
         raise PrincipalLookupError(id)

provideUtility(DummyAuthenticationUtility())


class SecurityTestCase(unittest.TestCase):

    def _get_interaction(self, uid):
        auth = getUtility(IAuthentication, context=None)

        interaction = ZopeSecurityPolicy()
        sess = SessionStub(auth.getPrincipal(uid))
        interaction.add(sess)
        return interaction

    def make_compute(self, hostname=u'tux-for-test', state=u'active', memory=2000):
        res = Compute(hostname, state, memory)
        res.architecture = 'linux'
        return res

    @run_in_reactor
    def test_test(self):
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
        with assert_raises(ForbiddenAttribute):
            eq_(compute_proxy_user1.state, 'active')