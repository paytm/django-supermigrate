# django-supermigrate

django-supermigrate is a package to manage migrations on production and development environment with no hassle.

##Idea

The main idea behind this project is to manage migration __simultaneously__ on development and production environment. The convention is, on __development__ environment, Django should be able to __run__ the migrations and hence the changes should be reflected in the database, whereas on production, the migrations should __not__ be allowed to run, hence they should not create any table on production. They should just create the __associated content types__ and the __permission__ and all the changes on the production, be it any create table or any alter, should go through the DBA.

##Problem

There was no generic way to control the migrations. Django provides a `managed` flag in the `Meta` class of the model, which decides whether the table should be created or not. This flag could have been helpful, if its value was picked from settings at run time. Settings can be split into `live` and `dev` settings. If the managed flag could pick the value from settings, then there was no problem.

So,

```
class Book(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = True if settings.MANAGED_FLAG else False
```

in settings,

```
# settings_dev.py
MANAGED_FLAG = True

# settings_live.py
MANAGED_FLAG = False
```

This worked for a while, but soon we realized that it was helpful in no way.
For each change in model, a migration file is created which remains same across the development and production environment. Now the above `if` in the managed flag works, but this is resolved only once when the `makemigrations` command is run. So if we create the migration on the development environment, then managed will be True in the generated migration file, but this will be True for production environment also. It can be dangerous if anyone runs by mistake migrations on the production.

One solution can be to run __makemigrations__ on production, using __settings_live__, and hence `managed` flag will be __False__. But that is highly __discouraged__. 
Another solution for this can be to keep separate value on `master` and `production` branch. But that becomes very messy to manage.


So how did we solve this problem?

##Solution

On looking deeper into the code, we first found out that there is a database router, which specifies database that will be used for reading, writing, allowing relation and __migrations__ corresponding to an app or model. The interesting function here is `allow_migrate` which takes db, app_label and model_name as argument. This allow_migrate is called for each model in each app. It checks whether on the given database, for a particular model in an app, are the migrations allowed to run? The more interesting thing is that it is not resolved once, infact it is resolved for each and every model in `INSTALLED_APPS`. So If somehow we can hook some checks in the `allow_migrate` which takes its value from settings, then our problem will be solved.

So we decided that for each model, we will keep its managed flag as __True__. There will be a flag in dev and live settings, which will specify whether the migrations should be allowed to run or not. On development, tables will be created by Django and on production, no migrations will be run as `allow_migrate` will return __False__ over there.

The first step in solving this problem was writing a __generic database router__ which takes a required mapping from settings, __DATABASE_ROUTER_MAPPING__. This is a mapping of app is to database, and it is necessary to specify database for every app, else it will not allow  migrations to run. It looks like,

```
DATABASE_ROUTER_MAPPING = {

    # default db
    "admin" : "default",
    "auth" : "default",
    "contenttypes" : "default",
    "sites" : "default",
    "sessions" : "default",

    # book_store db
    "book": "book_store"
}
```

Important thing that we observed here is that it is mandatory to specify the apps which uses __default__ db. This is because if apps corresponding to a default database are not specified, then when database argument is passed to migrate command like

```
python manage.py migrate --database=book_store
```

then it will create all auth and content types table in `book_store` database, which is not required at all.

To make it even more correct, we also wrote a utility function which checks its value from the settings. It throws an error if no database is specified for a app

```
def is_database_connection_in_settings(appname):

    if not hasattr(settings, 'DATABASE_ROUTER_MAPPING'):
        raise CommandError("DATABASE_ROUTER_MAPPING mapping missing from"
                           " settings")

    if appname.lower() in settings.DATABASE_ROUTER_MAPPING:
        return True
    else:
        raise CommandError("Database not specified for app {}. Please make"
                           " an entry in DATABASE_ROUTER_MAPPING in "
                           "settings".format(appname.lower()))n "
                           "settings".format(appname.lower()))
```


After this we wrote a utility function which check the value of managed_flag from the settings and it is like

```
def is_migrate_allowed():

    '''
    If settings is having ALLOW_MIGRATE_FALSE flag and its value is false,
    then return false, else return none.
    dev settings has no such flag, hence will return None in that case
    live setting has this flag as `False` hence will return False
    '''

    if hasattr(settings, 'ALLOW_MIGRATE_FALSE') and settings.ALLOW_MIGRATE_FALSE == False:
        return False
    return None
```

Our final ```allow_migrate``` looks something like this

```
def allow_migrate(self, db, app_label, model=None, **hints):
    '''
        gets managed flag value,
        if it is false, return false
        if it is None, means it is dev environment
    '''
    managed_flag = is_migrate_allowed()
    if managed_flag == False:
        return False

    if is_database_connection_in_settings(app_label):
        return db == settings.DATABASE_ROUTER_MAPPING[app_label]

    return None

```


This solved our problem to some extent. The only glitch that it brought is each database other than the default database will have a `django_migration` table. and we will run migrate command for each database, like

```
python manage.py migrate --database=book_store
python manage.py migrate --database=default
```

This brought us the need for supermigrate, which runs the migrate command for each key in `DATABASES` defined in `settings`.


Things were running fine uptill now, but we soon realized that there is no need for `django_migration` table in each database other than the default database. On production, we only need to run

```
python manage.py migrate --database=default
```

and all the changes will be reflected, but no such changes were there. Changes like creation of content_type and permission which are very useful. So what we were missing??

On closely observing that we realized that we have disabled migrations for each and every app, which also includes the `auth` and `contenttypes` app. These app are responsible for creating permission and content type and since the managed flag was False for each app on the production, no content type and permission was created.

So to deal with this problem, we followed a convention that,

```
By default no app will be allowed to migrate on production except some
```

To tackle this problem, we defined a `ALLOW_DB_MIGRATE` mapping in settings, which contains all those databases, where migrations are allowed to run, like

```
ALLOW_DB_MIGRATE = {
    'default': True
}
```

and then updated is_migrate_allowed to

```
def is_migrate_allowed(db):

    '''
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

```

Now the final version of allow_migrate looks like

```
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

```

Considering our settings are split across base, dev and live, the following should be there in settings

__base.py__
```
DATABASE_ROUTER_MAPPING = {
    # default db
    "admin" : "default",
    "auth" : "default",
    "contenttypes" : "default",
    "sites" : "default",
    "sessions" : "default",

    # book_store db
    "book": "book_store"

    # etc
}

DATABASE_ROUTERS  = [ 'supermigrate.database_routers.default.DefaultRouter', ]

```

__settings_dev.py__
```
# nothing here as we want migrations to run
```

__settings_live.py__
```
ALLOW_MIGRATE_FALSE = False

ALLOW_DB_MIGRATE = {
    'default': True
}

```
