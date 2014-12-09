# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djcelery.picklefield


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CrontabSchedule',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('minute', models.CharField(default='*', max_length=64, verbose_name='minute')),
                ('hour', models.CharField(default='*', max_length=64, verbose_name='hour')),
                ('day_of_week', models.CharField(default='*', max_length=64, verbose_name='day of week')),
                ('day_of_month', models.CharField(default='*', max_length=64, verbose_name='day of month')),
                ('month_of_year', models.CharField(default='*', max_length=64, verbose_name='month of year')),
            ],
            options={
                'ordering': ['month_of_year', 'day_of_month', 'day_of_week', 'hour', 'minute'],
                'verbose_name_plural': 'crontabs',
                'verbose_name': 'crontab',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntervalSchedule',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('every', models.IntegerField(verbose_name='every')),
                ('period', models.CharField(max_length=24, verbose_name='period', choices=[('days', 'Days'), ('hours', 'Hours'), ('minutes', 'Minutes'), ('seconds', 'Seconds'), ('microseconds', 'Microseconds')])),
            ],
            options={
                'ordering': ['period', 'every'],
                'verbose_name_plural': 'intervals',
                'verbose_name': 'interval',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeriodicTask',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Useful description', max_length=200, unique=True, verbose_name='name')),
                ('task', models.CharField(max_length=200, verbose_name='task name')),
                ('args', models.TextField(default='[]', verbose_name='Arguments', blank=True, help_text='JSON encoded positional arguments')),
                ('kwargs', models.TextField(default='{}', verbose_name='Keyword arguments', blank=True, help_text='JSON encoded keyword arguments')),
                ('queue', models.CharField(default=None, max_length=200, help_text='Queue defined in CELERY_QUEUES', blank=True, null=True, verbose_name='queue')),
                ('exchange', models.CharField(default=None, max_length=200, blank=True, null=True, verbose_name='exchange')),
                ('routing_key', models.CharField(default=None, max_length=200, blank=True, null=True, verbose_name='routing key')),
                ('expires', models.DateTimeField(blank=True, null=True, verbose_name='expires')),
                ('enabled', models.BooleanField(default=True, verbose_name='enabled')),
                ('last_run_at', models.DateTimeField(blank=True, null=True, editable=False)),
                ('total_run_count', models.PositiveIntegerField(default=0, editable=False)),
                ('date_changed', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('crontab', models.ForeignKey(help_text='Use one of interval/crontab', blank=True, null=True, to='djcelery.CrontabSchedule', verbose_name='crontab')),
                ('interval', models.ForeignKey(blank=True, null=True, to='djcelery.IntervalSchedule', verbose_name='interval')),
            ],
            options={
                'verbose_name_plural': 'periodic tasks',
                'verbose_name': 'periodic task',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeriodicTasks',
            fields=[
                ('ident', models.SmallIntegerField(primary_key=True, default=1, unique=True, serialize=False)),
                ('last_update', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskMeta',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(max_length=255, unique=True, verbose_name='task id')),
                ('status', models.CharField(default=b'PENDING', max_length=50, verbose_name='state', choices=[(b'RECEIVED', b'RECEIVED'), (b'STARTED', b'STARTED'), (b'REVOKED', b'REVOKED'), (b'PENDING', b'PENDING'), (b'SUCCESS', b'SUCCESS'), (b'FAILURE', b'FAILURE'), (b'RETRY', b'RETRY')])),
                ('result', djcelery.picklefield.PickledObjectField(default=None, editable=False, null=True)),
                ('date_done', models.DateTimeField(auto_now=True, verbose_name='done at')),
                ('traceback', models.TextField(blank=True, null=True, verbose_name='traceback')),
                ('hidden', models.BooleanField(default=False, db_index=True, editable=False)),
                ('meta', djcelery.picklefield.PickledObjectField(default=None, editable=False, null=True)),
            ],
            options={
                'verbose_name_plural': 'task states',
                'verbose_name': 'task state',
                'db_table': 'celery_taskmeta',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskSetMeta',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('taskset_id', models.CharField(max_length=255, unique=True, verbose_name='group id')),
                ('result', djcelery.picklefield.PickledObjectField(editable=False)),
                ('date_done', models.DateTimeField(auto_now=True, verbose_name='created at')),
                ('hidden', models.BooleanField(default=False, db_index=True, editable=False)),
            ],
            options={
                'verbose_name_plural': 'saved group results',
                'verbose_name': 'saved group result',
                'db_table': 'celery_tasksetmeta',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskState',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=64, db_index=True, choices=[(b'RECEIVED', b'RECEIVED'), (b'STARTED', b'STARTED'), (b'REVOKED', b'REVOKED'), (b'PENDING', b'PENDING'), (b'SUCCESS', b'SUCCESS'), (b'FAILURE', b'FAILURE'), (b'RETRY', b'RETRY')], verbose_name='state')),
                ('task_id', models.CharField(max_length=36, unique=True, verbose_name='UUID')),
                ('name', models.CharField(max_length=200, db_index=True, null=True, verbose_name='name')),
                ('tstamp', models.DateTimeField(db_index=True, verbose_name='event received at')),
                ('args', models.TextField(verbose_name='Arguments', null=True)),
                ('kwargs', models.TextField(verbose_name='Keyword arguments', null=True)),
                ('eta', models.DateTimeField(verbose_name='ETA', null=True)),
                ('expires', models.DateTimeField(verbose_name='expires', null=True)),
                ('result', models.TextField(verbose_name='result', null=True)),
                ('traceback', models.TextField(verbose_name='traceback', null=True)),
                ('runtime', models.FloatField(verbose_name='execution time', null=True, help_text='in seconds if task succeeded')),
                ('retries', models.IntegerField(default=0, verbose_name='number of retries')),
                ('hidden', models.BooleanField(default=False, db_index=True, editable=False)),
            ],
            options={
                'ordering': ['-tstamp'],
                'get_latest_by': 'tstamp',
                'verbose_name_plural': 'tasks',
                'verbose_name': 'task',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WorkerState',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=255, unique=True, verbose_name='hostname')),
                ('last_heartbeat', models.DateTimeField(db_index=True, verbose_name='last heartbeat', null=True)),
            ],
            options={
                'ordering': ['-last_heartbeat'],
                'get_latest_by': 'last_heartbeat',
                'verbose_name_plural': 'workers',
                'verbose_name': 'worker',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='taskstate',
            name='worker',
            field=models.ForeignKey(null=True, to='djcelery.WorkerState', verbose_name='worker'),
            preserve_default=True,
        ),
    ]
