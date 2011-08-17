from grokcore.component import baseclass, context
from zope.component import provideSubscriptionAdapter
import argparse
import os

from opennode.oms.endpoint.ssh import cmd
from opennode.oms.endpoint.ssh.completion import Completer
from opennode.oms.endpoint.ssh.cmdline import GroupDictAction
from opennode.oms.model.model.base import IContainer
from opennode.oms.model.model import creatable_models
from opennode.oms.zodb import db


class CommandCompleter(Completer):
    """Completes a command."""

    context(cmd.NoCommand)

    def complete(self, token, parsed, parser):
        return [name for name in cmd.commands().keys() if name.startswith(token)]


class PathCompleter(Completer):
    """Completes a path name."""
    baseclass()

    @db.transact
    def complete(self, token, parsed, parser):
        if not self.consumed(parsed, parser):
            base_path = os.path.dirname(token)
            container = self.context.traverse(base_path)

            if IContainer.providedBy(container):
                def dir_suffix(obj):
                    return '/' if IContainer.providedBy(obj) else ''

                def name(obj):
                    return os.path.join(base_path, obj.__name__)

                return [name(obj) + dir_suffix(obj) for obj in container.listcontent() if name(obj).startswith(token)]


        return []

    def consumed(self, parsed, parser):
        """Check whether we have already consumed all positional arguments."""

        maximum = 0
        actual = 0
        for action_group in parser._action_groups:
            for action in action_group._group_actions:
                # For every positional argument:
                if not action.option_strings:
                    # Count how many of them we have already.
                    values = getattr(parsed, action.dest, [])
                    if values == action.default:  # don't count default values
                        values = []
                    if not isinstance(values, list):
                        values = [values]
                    actual += len(values)

                    # And the maximum number of expected occurencies.
                    if action.nargs is None:
                        maximum += 1
                    elif isinstance(action.nargs, int):
                        maximum += action.nargs
                    elif action.nargs == argparse.OPTIONAL:
                        maximum += 1
                    else:
                        maximum = float('inf')

        return actual >= maximum


class ArgSwitchCompleter(Completer):
    """Completes argument switches based on the argparse grammar exposed for a command"""
    baseclass()

    def complete(self, token, parsed, parser):
        if token.startswith("-"):
            parser = self.context.arg_parser(partial=True)

            options = [option
                       for action_group in parser._action_groups
                       for action in action_group._group_actions
                       for option in action.option_strings
                       if option.startswith(token) and not self.option_consumed(action, parsed)]
            return options
        else:
            return []

    def option_consumed(self, action, parsed):
        # "count" actions can be repeated
        if action.nargs > 0 or isinstance(action, argparse._CountAction):
            return False

        if isinstance(action, GroupDictAction):
            value = getattr(parsed, action.group, {}).get(action.dest, action.default)
        else:
            value = getattr(parsed, action.dest, action.default)

        return value != action.default

class KeywordSwitchCompleter(ArgSwitchCompleter):
    """Completes key=value argument switches based on the argparse grammar exposed for a command.
    TODO: probably more can be shared with ArgSwitchCompleter."""

    baseclass()

    def complete(self, token, parsed, parser):
        options = [option[1:] + '='
                   for action_group in parser._action_groups
                   for action in action_group._group_actions
                   for option in action.option_strings
                   if option.startswith('=' + token) and not self.option_consumed(action, parsed)]
        return options


class KeywordValueCompleter(ArgSwitchCompleter):
    """Completes the `value` part of key=value constructs based on the type of the keyword.
    Currently works only for args which declare an explicit enumeration."""

    baseclass()

    def complete(self, token, parsed, parser):
        if '=' in token:
            keyword, value_prefix = token.split('=')

            action = self.find_action(keyword, parsed, parser)
            if action.choices:
                return [keyword + '=' + value for value in action.choices if value.startswith(value_prefix)]

        return []

    def find_action(self, keyword, parsed, parser):
        for action_group in parser._action_groups:
            for action in action_group._group_actions:
                if action.dest == keyword:
                    return action


class ObjectTypeCompleter(Completer):
    """Completes object type names."""

    context(cmd.cmd_mk)

    def complete(self, token, parsed, parser):
        return [name for name in creatable_models.keys() if name.startswith(token)]


# TODO: move to handler
for command in [cmd.cmd_ls, cmd.cmd_cd, cmd.cmd_cat, cmd.cmd_set]:
    provideSubscriptionAdapter(PathCompleter, adapts=[command])

for command in [cmd.cmd_ls, cmd.cmd_cd, cmd.cmd_cat, cmd.cmd_set, cmd.cmd_quit]:
    provideSubscriptionAdapter(ArgSwitchCompleter, adapts=[command])

for command in [cmd.cmd_set]:
    provideSubscriptionAdapter(KeywordSwitchCompleter, adapts=[command])

for command in [cmd.cmd_set]:
    provideSubscriptionAdapter(KeywordValueCompleter, adapts=[command])
