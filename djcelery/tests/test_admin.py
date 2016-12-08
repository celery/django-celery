from __future__ import unicode_literals

from django.contrib import admin
from django.test import RequestFactory, TestCase

from djcelery.admin import PeriodicTaskAdmin
from djcelery.models import (
    PeriodicTask, IntervalSchedule, PERIOD_CHOICES, PeriodicTasks
)


class MockRequest(object):
    pass


request = MockRequest()

site = admin.AdminSite()


class TestPeriodicTaskAdmin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.interval = IntervalSchedule.objects.create(
            every=1, period=PERIOD_CHOICES[0][0])

        cls.request_factory = RequestFactory()

        cls.pt_admin = PeriodicTaskAdmin(PeriodicTask, site)

    def test_specified_ordering(self):
        """
        Ordering should be by ('-enabled', 'name')
        """
        PeriodicTask.objects.bulk_create([
            PeriodicTask(name='Bohemian Rhapsody', task='bohemian_rhapsody',
                         interval=self.interval, enabled=True),
            PeriodicTask(name='Somebody to Love', task='somebody_to_love',
                         interval=self.interval, enabled=False),
            PeriodicTask(name='Tie Your Mother Down',
                         task='tie_your_mother_down',
                         interval=self.interval, enabled=False),
            PeriodicTask(name='Under Pressure', task='under_pressure',
                         interval=self.interval, enabled=True),
        ])
        names = [b.name for b in self.pt_admin.get_queryset(request)]
        self.assertListEqual(['Bohemian Rhapsody', 'Under Pressure',
                              'Somebody to Love', 'Tie Your Mother Down'],
                             names)

    def test_enable_tasks_should_enable_disabled_periodic_tasks(self):
        """
        enable_tasks action should enable selected periodic tasks
        """
        PeriodicTask.objects.create(name='Killer Queen', task='killer_queen',
                                    interval=self.interval, enabled=False),
        queryset = PeriodicTask.objects.filter(pk=1)
        last_update = PeriodicTasks.objects.get(ident=1).last_update
        self.pt_admin.enable_tasks(request, queryset)
        new_last_update = PeriodicTasks.objects.get(ident=1).last_update
        self.assertTrue(PeriodicTask.objects.get(pk=1).enabled)
        self.assertNotEqual(last_update, new_last_update)

    def test_disable_tasks_should_disable_enabled_periodic_tasks(self):
        """
        disable_tasks action should disable selected periodic tasks
        """
        PeriodicTask.objects.create(name='Killer Queen', task='killer_queen',
                                    interval=self.interval, enabled=True),
        queryset = PeriodicTask.objects.filter(pk=1)
        self.pt_admin.disable_tasks(request, queryset)
        self.assertFalse(PeriodicTask.objects.get(pk=1).enabled)

    def test_for_valid_search_fields(self):
        """
        Valid search fields should be ('name', 'task')
        """
        search_fields = self.pt_admin.search_fields
        self.assertEqual(search_fields, ('name', 'task'))

        for fieldname in search_fields:
            query = '%s__icontains' % fieldname
            kwargs = {query: 'Queen'}
            # We have no content, so the number of results if we search on
            # something should be zero.
            self.assertEquals(PeriodicTask.objects.filter(**kwargs).count(), 0)
