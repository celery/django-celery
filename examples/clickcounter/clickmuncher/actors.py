from collections import defaultdict

import cl

from celery import current_app as celery
from celery.utils.timer2 import apply_interval


from clickmuncher import models


class Clicks(cl.Actor):
    default_routing_key = "Clicks"

    class state:
        model = models.Click
        clicks = defaultdict(lambda: 0)

        def increment(self, url, clicks=1):
            self.clicks[url] += clicks

        def flush(self):
            print("FLUSH!!!")
            print("STATE: %r" % (self.clicks, ))
            for url, clicks in self.clicks.iteritems():
                self.model.objects.increment_clicks(url, clicks)
            self.clicks.clear()

    def __init__(self, connection=None, *args, **kwargs):
        if not connection:
            connection = celery.broker_connection()
        super(Clicks, self).__init__(connection, *args, **kwargs)

    def increment(self, url, clicks=1):
        self.cast("increment", {"url": url, "clicks": clicks})


class Agent(cl.Agent):
    actors = [Clicks()]
    flush_every = 5

    def __init__(self, connection=None, *args, **kwargs):
        if not connection:
            connection = celery.broker_connection()
        self.clicks = Clicks()
        self.actors = [self.clicks]
        self.timers = []
        super(Agent, self).__init__(connection, *args, **kwargs)

    def on_consume_ready(self, *args, **kwargs):
        print("INSTALLING TIMER")
        self.timers.append(apply_interval(self.flush_every * 1000,
                                          self.clicks.state.flush))

    def stop(self):
        for entry in self.timers:
            entry.cancel()
        super(Agent, self).stop()


if __name__ == "__main__":
    Agent().run_from_commandline()
