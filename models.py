from django.conf import settings
from django.db import models


class OauthSignOut(models.Model):
    application = models.OneToOneField(settings.OAUTH2_PROVIDER_APPLICATION_MODEL)
    signout_uri = models.CharField(max_length=200)

    def __str__(self):
        return self.application.name
