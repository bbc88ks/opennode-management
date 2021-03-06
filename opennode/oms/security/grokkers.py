import grokcore.security
import martian

from zope.security.checker import defineChecker

from opennode.oms.config import get_config
from opennode.oms.security.checker import Checker, AuditingPermissionDictionary
from opennode.oms.security.directives import permissions


class SecurityGrokker(martian.ClassGrokker):
    martian.component(object)
    martian.directive(permissions, name='permissions')

    def execute(self, factory, config, permissions, **kw):
        if not permissions:
            return False

        if get_config().getboolean('auth', 'enforce_attribute_rights_definition'):
            perms = {}
        else:
            perms = AuditingPermissionDictionary()

        # mandatory, otherwise zope's default Checker impl will be used
        # which doesn't play well with Twisted.
        defineChecker(factory, Checker(perms, perms))

        # TODO: supply the 'inherit' option to the class somehow
        # to facilitate optional inheritance of all permissions
        for class_inheritance_level in permissions:
            for name, permission in class_inheritance_level.items():
                if isinstance(permission, tuple):
                    read_perm, write_perm = permission
                    config.action(discriminator=('protectNameSet', factory, name),
                                  callable=grokcore.security.util.protect_setattr,
                                  args=(factory, name, write_perm))
                else:
                    read_perm = permission

                config.action(discriminator=('protectName', factory, name),
                              callable=grokcore.security.util.protect_getattr,
                              args=(factory, name, read_perm))

        return True
