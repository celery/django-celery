from django.db import models
from django.utils.translation import ugettext_lazy as _
from djcelery.managers import ExtendedManager


class ClickManager(ExtendedManager):

    def increment_clicks(self, url, increment=1):
        """Increment the click count for an URL."""
        obj, created = self.get_or_create(url=url,
                                    defaults={"clicks": increment})
        if not created:
            obj.clicks += increment
            obj.save()

        return obj.clicks


class Click(models.Model):
    url = models.URLField(_(u"URL"), verify_exists=False, unique=True)
    clicks = models.PositiveIntegerField(_(u"clicks"), default=0)

    objects = ClickManager()

    class Meta:
        verbose_name = _(u"click")
        verbose_name_plural = _(u"clicks")
