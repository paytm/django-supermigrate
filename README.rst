===================
Django Supermigrate
===================

Django Supermigrate is a package to manage migrations on production and development environment with no hassle.

Quick start
-----------

1. Add "supermigrate" to your INSTALLED_APPS like this::

    ```
    INSTALLED_APPS = (
        ...
        'supermigrate',
    )
    ```

2. Modify your DATABASE_ROUTERS to include 'default' router like this::

    ```
    DATABASE_ROUTERS  = [ 'supermigrate.database_routers.default.DefaultRouter', ]
    ```

3. Add DATABASE_ROUTER_MAPPING in settings like this::

    ```
        DATABASE_ROUTER_MAPPING = {

            # default db
            "admin" : {
                "DB_FOR_READ": "default_slave",
                "DB_FOR_WRITE": "default",
                "DB_FOR_MIGRATE": ["default", "default_slave"]
            },
            "auth" : {
                "DB_FOR_READ": "default",
                "DB_FOR_WRITE": "default",
                "DB_FOR_MIGRATE": ["default", "default_slave"]
            }

            # other db here

        }
    ```

4. Update settings for live with ::

    ```
    ALLOW_MIGRATE_FALSE = False

    ALLOW_DB_MIGRATE = {
        'default': True
    }
    ```
