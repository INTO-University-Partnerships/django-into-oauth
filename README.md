# Django INTO OAuth

A Django app that allows Django to act as an OAuth [IdP](http://en.wikipedia.org/wiki/Identity_provider).

Commands are relative to the directory in which Django is installed.

## Dependencies

* Python 2.7 or 3.4
* Django 1.7
* [Django](https://github.com/evonove/django-oauth-toolkit) [OAuth](https://django-oauth-toolkit.readthedocs.org/en/latest/) [Toolkit](https://pypi.python.org/pypi/django-oauth-toolkit) 0.9.0

## Installation

    pip install django-oauth-toolkit==0.9.0
    git clone https://github.com/INTO-University-Partnerships/django-into-oauth into_oauth

In `settings.py`, add the following to `INSTALLED_APPS`:

    'oauth2_provider',
    'into_oauth'

In `settings.py`, add the following to `AUTHENTICATION_BACKENDS`:

    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend'

In `settings.py`, add the following to `MIDDLEWARE_CLASSES`:

    'oauth2_provider.middleware.OAuth2TokenMiddleware'

In `settings.py`, add the following:

    INTO_OAUTH_USERDATA = {
        'username': 'username',
        'email': 'email',
        'first_name': 'first_name',
        'last_name': 'last_name'
    }

    OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'

In the project's `urls.py`, add the following:

    url(r'^o/', include('into_oauth.urls', namespace='oauth2_provider')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url(r'^accounts/', include('django.contrib.auth.urls'))

Run migrations:

    ./manage.py migrate

## Configuration

Login to the Django admin.

At `/admin`, under `Oauth2_Provider`, add a new `Application` with the following fields:

    Client ID: auto-generated
    User: set to an admin user
    Redirect uris: the consumer's login endpoint, e.g. /auth/oauth/login/ relative to a Moodle's wwwroot
    Client type: Confidential
    Authorization grant type: Authorization code
    Client secret: auto-generated
    Name: an arbitrary name

At `/admin`, under `Into_Oauth`, add a new `Oauth sign outs` with the following fields:

    Application: set to the arbitrary name of the above Application
    Signout uri: the consumer's logout endpoint, e.g. /auth/oauth/logout/ relative to a Moodle's wwwroot

## Tests

Configure a `pytest.ini`, then:

    pip install pytest-django pytest-sugar pytest-cache
    py.test into_oauth
