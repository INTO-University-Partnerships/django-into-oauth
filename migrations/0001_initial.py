# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OauthSignOut',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signout_uri', models.CharField(max_length=200)),
                ('application', models.OneToOneField(to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
