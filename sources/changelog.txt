================
 Change history
================

2.0.2
=====

Important notes
---------------

* Due to some applications loading the Django models lazily, it is recommended
  that you add the following lines to your ``settings.py``::

       import djcelery
       djcelery.setup_loader()

    This will ensure the Django celery loader is set even though the
    model modules haven't been imported yet.

News
----

* ``djcelery.views.registered_tasks``: Added a view to list currently known
  tasks.

2.0.0
=====
:release-date: 2010-07-02 02:30 P.M CEST

* Initial release
