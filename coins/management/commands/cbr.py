# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Scan cbr site'

    def handle(self, *args, **options):
        self.stdout.write('Snaning')