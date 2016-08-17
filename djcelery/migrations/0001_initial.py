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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('minute', models.CharField(default='*', max_length=64, verbose_name='minute')),
                ('hour', models.CharField(default='*', max_length=64, verbose_name='hour')),
                ('day_of_week', models.CharField(default='*', max_length=64, verbose_name='day of week')),
                ('day_of_month', models.CharField(default='*', max_length=64, verbose_name='day of month')),
                ('month_of_year', models.CharField(default='*', max_length=64, verbose_name='month of year')),
            ],
            options={
                'ordering': ['month_of_year', 'day_of_month', 'day_of_week', 'hour', 'minute'],
                'verbose_name': 'crontab',
                'verbose_name_plural': 'crontabs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntervalSchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('every', models.IntegerField(verbose_name='every')),
                ('period', models.CharField(max_length=24, verbose_name='period', choices=[('days', 'Days'), ('hours', 'Hours'), ('minutes', 'Minutes'), ('seconds', 'Seconds'), ('microseconds', 'Microseconds')])),
            ],
            options={
                'ordering': ['period', 'every'],
                'verbose_name': 'interval',
                'verbose_name_plural': 'intervals',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeriodicTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Useful description', unique=True, max_length=200, verbose_name='name')),
                ('task', models.CharField(max_length=200, verbose_name='task name')),
                ('args', models.TextField(default='[]', help_text='JSON encoded positional arguments', verbose_name='Arguments', blank=True)),
                ('kwargs', models.TextField(default='{}', help_text='JSON encoded keyword arguments', verbose_name='Keyword arguments', blank=True)),
                ('queue', models.CharField(default=None, max_length=200, blank=True, help_text='Queue defined in CELERY_QUEUES', null=True, verbose_name='queue')),
                ('exchange', models.CharField(default=None, max_length=200, null=True, verbose_name='exchange', blank=True)),
                ('routing_key', models.CharField(default=None, max_length=200, null=True, verbose_name='routing key', blank=True)),
                ('expires', models.DateTimeField(null=True, verbose_name='expires', blank=True)),
                ('enabled', models.BooleanField(default=True, verbose_name='enabled')),
                ('last_run_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('total_run_count', models.PositiveIntegerField(default=0, editable=False)),
                ('date_changed', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('crontab', models.ForeignKey(blank=True, to='djcelery.CrontabSchedule', help_text='Use one of interval/crontab', null=True, verbose_name='crontab', on_delete=models.CASCADE)),
                ('interval', models.ForeignKey(verbose_name='interval', blank=True, to='djcelery.IntervalSchedule', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'periodic task',
                'verbose_name_plural': 'periodic tasks',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeriodicTasks',
            fields=[
                ('ident', models.SmallIntegerField(default=1, unique=True, serialize=False, primary_key=True)),
                ('last_update', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_id', models.CharField(unique=True, max_length=255, verbose_name='task id')),
                ('status', models.CharField(default='PENDING', max_length=50, verbose_name='state', choices=[('FAILURE', 'FAILURE'), ('PENDING', 'PENDING'), ('RECEIVED', 'RECEIVED'), ('RETRY', 'RETRY'), ('REVOKED', 'REVOKED'), ('STARTED', 'STARTED'), ('SUCCESS', 'SUCCESS')])),
                ('result', djcelery.picklefield.PickledObjectField(default=None, null=True, editable=False)),
                ('date_done', models.DateTimeField(auto_now=True, verbose_name='done at')),
                ('traceback', models.TextField(null=True, verbose_name='traceback', blank=True)),
                ('hidden', models.BooleanField(default=False, db_index=True, editable=False)),
                ('meta', djcelery.picklefield.PickledObjectField(default=None, null=True, editable=False)),
            ],
            options={
                'db_table': 'celery_taskmeta',
                'verbose_name': 'task state',
                'verbose_name_plural': 'task states',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskSetMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('taskset_id', models.CharField(unique=True, max_length=255, verbose_name='group id')),
                ('result', djcelery.picklefield.PickledObjectField(editable=False)),
                ('date_done', models.DateTimeField(auto_now=True, verbose_name='created at')),
                ('hidden', models.BooleanField(default=False, db_index=True, editable=False)),
            ],
            options={
                'db_table': 'celery_tasksetmeta',
                'verbose_name': 'saved group result',
                'verbose_name_plural': 'saved group results',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(db_index=True, max_length=64, verbose_name='state', choices=[('FAILURE', 'FAILURE'), ('PENDING', 'PENDING'), ('RECEIVED', 'RECEIVED'), ('RETRY', 'RETRY'), ('REVOKED', 'REVOKED'), ('STARTED', 'STARTED'), ('SUCCESS', 'SUCCESS')])),
                ('task_id', models.CharField(unique=True, max_length=36, verbose_name='UUID')),
                ('name', models.CharField(max_length=200, null=True, verbose_name='name', db_index=True)),
                ('tstamp', models.DateTimeField(verbose_name='event received at', db_index=True)),
                ('args', models.TextField(null=True, verbose_name='Arguments')),
                ('kwargs', models.TextField(null=True, verbose_name='Keyword arguments')),
                ('eta', models.DateTimeField(null=True, verbose_name='ETA')),
                ('expires', models.DateTimeField(null=True, verbose_name='expires')),
                ('result', models.TextField(null=True, verbose_name='result')),
                ('traceback', models.TextField(null=True, verbose_name='traceback')),
                ('runtime', models.FloatField(help_text='in seconds if task succeeded', null=True, verbose_name='execution time')),
                ('retries', models.IntegerField(default=0, verbose_name='number of retries')),
                ('hidden', models.BooleanField(default=False, db_index=True, editable=False)),
            ],
            options={
                'ordering': ['-tstamp'],
                'get_latest_by': 'tstamp',
                'verbose_name': 'task',
                'verbose_name_plural': 'tasks',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WorkerState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(unique=True, max_length=255, verbose_name='hostname')),
                ('last_heartbeat', models.DateTimeField(null=True, verbose_name='last heartbeat', db_index=True)),
            ],
            options={
                'ordering': ['-last_heartbeat'],
                'get_latest_by': 'last_heartbeat',
                'verbose_name': 'worker',
                'verbose_name_plural': 'workers',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='taskstate',
            name='worker',
            field=models.ForeignKey(verbose_name='worker', to='djcelery.WorkerState', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
