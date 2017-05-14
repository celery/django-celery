# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djcelery', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskmeta',
            name='task_id',
            field=models.CharField(unique=True, max_length=36, verbose_name='task id'),
        ),
    ]
