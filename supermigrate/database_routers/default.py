from django.conf import settings

from ..utils import is_database_connection_in_settings, is_migrate_allowed


class DefaultRouter(object):
    """
    A router to control all database operations on models for
    each application.
    """

    def db_for_read(self, model, **hints):
        if is_database_connection_in_settings(model._meta.app_label):
            return settings.DATABASE_ROUTER_MAPPING[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        if is_database_connection_in_settings(model._meta.app_label):
            return settings.DATABASE_ROUTER_MAPPING[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if is_database_connection_in_settings(obj1._meta.app_label) or is_database_connection_in_settings(obj2._meta.app_label):
           return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        '''
            gets managed flag value,
            if it is false, return false
            if it is None, means it is dev environment
        '''
        managed_flag = is_migrate_allowed(db)
        if managed_flag == False:
            return False

        if is_database_connection_in_settings(app_label):
            return db == settings.DATABASE_ROUTER_MAPPING[app_label]

        return None
