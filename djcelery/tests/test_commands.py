# coding: utf-8
from django import VERSION
from django.core.management import call_command

from ._compat import patch


CELERYD_COMMAND = 'djcelery.management.commands.celeryd.Command.handle'


def test_celeryd_command():
    if VERSION >= (1, 10):
        traceback = False
    else:
        traceback = None
    with patch(CELERYD_COMMAND) as handle:
        call_command('celeryd')
        handle.assert_called_with(
            autoreload=None, autoscale=None, beat=None, broker=None,
            concurrency=0, detach=None, exclude_queues=[], executable=None,
            gid=None, heartbeat_interval=None, hostname=None, include=[],
            logfile=None, loglevel='WARN', max_tasks_per_child=None,
            no_color=False, no_execv=False, optimization=None, pidfile=None,
            pool_cls='prefork', purge=False, pythonpath=None, queues=[],
            quiet=None, schedule_filename='celerybeat-schedule',
            scheduler_cls=None, send_events=False, settings=None,
            skip_checks=True, state_db=None, task_soft_time_limit=None,
            task_time_limit=None, traceback=traceback, uid=None, umask=None,
            verbosity=1, without_gossip=False, without_heartbeat=False,
            without_mingle=False, working_directory=None
        )
