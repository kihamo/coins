from django.core.management.base import BaseCommand as DjangoBaseCommand
from django.utils.encoding import force_str


class BaseCommand(DjangoBaseCommand):
    def __init__(self):
        super(BaseCommand, self).__init__()
        self.verbosity = 1

    def _print_message(self, message, *args, **kwargs):
        message = force_str(force_str(message) % args)

        std = kwargs['std'] if 'std' in kwargs else self.stderr

        if 'style' in kwargs:
            message = kwargs['style'](message)

        if not 'level' in kwargs or self.verbosity >= kwargs['level']:
            std.write(message)

    def _error(self, message, *args, **kwargs):
        kwargs['style'] = self.style.ERROR
        self._print_message(message, *args, **kwargs)

    def _notice(self, message, *args, **kwargs):
        kwargs['style'] = self.style.NOTICE
        self._print_message(message, *args, **kwargs)

    def _info(self, message, *args, **kwargs):
        kwargs['std'] = self.stdout

        if not 'level' in kwargs:
            kwargs['level'] = 1

        self._print_message(message, *args, **kwargs)
