from django.core.management.base import CommandError
from django.conf import settings

def is_migrate_allowed(db):

    '''
    first check for ALLOW_DB_MIGRATE mapping, if this is having True for 
    current database,  then return True
    If settings is having ALLOW_MIGRATE_FALSE flag and its value is false,
    then return false, else return none.
    dev settings has no such flag, hence will return None in that case
    live setting has this flag as `False` hence will return False
    '''

    if hasattr(settings, 'ALLOW_DB_MIGRATE') and db in settings.ALLOW_DB_MIGRATE:
        return settings.ALLOW_DB_MIGRATE[db]

    if hasattr(settings, 'ALLOW_MIGRATE_FALSE') and settings.ALLOW_MIGRATE_FALSE == False:
        return False
    return None


def is_database_connection_in_settings(appname):
    ''' returns database corresponding to a app
        In future, this may also work on model
    '''

    if not hasattr(settings, 'DATABASE_ROUTER_MAPPING'):
        raise CommandError("DATABASE_ROUTER_MAPPING mapping missing from settings")

    if appname.lower() in settings.DATABASE_ROUTER_MAPPING:
        return True
    else:
        raise CommandError("Database not specified for app {}. Please make"
                           " an entry in DATABASE_ROUTER_MAPPING in "
                           "settings".format(appname.lower()))