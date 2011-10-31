from __future__ import absolute_import

import martian
from grokcore.component import Subscription, baseclass, querySubscriptions
from zope.interface import implements

from .base import IContainerExtender, ReadonlyContainer
from .bin import ICommand, Command


class ActionsContainer(ReadonlyContainer):
    """Implements a dynamic view containing commands
    representing actions that can be performer on a given object.

    """

    __name__ = 'actions'

    def __init__(self, parent):
        self.__parent__ = parent

    def content(self):
        actions = querySubscriptions(self.__parent__, ICommand)
        return dict((i._name, Command(i._name, self, i.cmd)) for i in actions)


class ActionsContainerExtension(Subscription):
    implements(IContainerExtender)
    baseclass()

    def extend(self):
        return {'actions': ActionsContainer(self.context)}


class Action(Subscription):
    implements(ICommand)
    baseclass()


class action(martian.Directive):
    """Use this directive on adapters used to define actions for specific model objects."""
    scope = martian.CLASS
    store = martian.ONCE
    default = None


class ActionGrokker(martian.ClassGrokker):
    martian.component(Subscription)
    martian.directive(action)

    def execute(self, class_, action, **kw):
        if action is None:
            return False

        class_.cmd = _action_decorator(class_.execute)
        class_._name = action

        return True


def _action_decorator(fun):
    """
    Decorate a method so that it behaves as a property which returns a Cmd object.
    """
    @property
    def cmd(self):
        from opennode.oms.endpoint.ssh.cmd.base import Cmd

        this = self

        class ActionCmd(Cmd):
            name = self._name

            def execute(self, args):
                return fun(this, self, args)
        return ActionCmd
    return cmd