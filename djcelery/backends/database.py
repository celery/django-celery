from celery import conf
from celery.backends.base import BaseDictBackend

from djcelery.models import TaskMeta, TaskSetMeta


class DatabaseBackend(BaseDictBackend):
    """The database backend.

    Using Django models to store task state.

    """
    TaskModel = TaskMeta
    TaskSetModel = TaskSetMeta
    expires = conf.TASK_RESULT_EXPIRES

    def _store_result(self, task_id, result, status, traceback=None):
        """Store return value and status of an executed task."""
        self.TaskModel._default_manager.store_result(task_id, result, status,
                                                     traceback=traceback)
        return result

    def _save_taskset(self, taskset_id, result):
        """Store the result of an executed taskset."""
        self.TaskSetModel._default_manager.store_result(taskset_id, result)
        return result

    def _get_task_meta_for(self, task_id):
        """Get task metadata for a task by id."""
        return self.TaskModel._default_manager.get_task(task_id).to_dict()

    def _restore_taskset(self, taskset_id):
        """Get taskset metadata for a taskset by id."""
        meta = self.TaskSetModel._default_manager.restore_taskset(taskset_id)
        if meta:
            return meta.to_dict()

    def _forget(self, task_id):
        try:
            self.TaskModel._default_manager.get(task_id=task_id).delete()
        except self.TaskModel.DoesNotExist:
            pass

    def cleanup(self):
        """Delete expired metadata."""
        for model in self.TaskModel, self.TaskSetModel:
            model._default_manager.delete_expired(self.expires)
