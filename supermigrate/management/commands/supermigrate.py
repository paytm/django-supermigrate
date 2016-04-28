import os
import subprocess

from os.path import join

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    '''This will run migrations for all app on all databases'''

    help = 'Applies migration for all app on all databases'
    can_import_settings = True

    def handle(self, *args, **options):

        manage_location = join(os.getcwd(), 'manage.py')
        # this assumes that virtualenv named `pyenv` exists
        python_path = join(os.getcwd(), 'pyenv', 'bin', 'python')
        databases = settings.DATABASES
        for name, connection_value in databases.items():
            subprocess.Popen([python_path, manage_location, 'migrate', '--noinput', '--database={}'.format(name)], env=os.environ)
