from django.utils import translation
from django.utils.functional import wraps

def respects_language(func):
    '''
    Decorator for tasks with respect to site's current language.
    You can use this decorator in tasks.py together with default @task decorator
    Be sure that task method have kwargs argument:

        @task
        @respects_language
        def my_task(any_optional_arguments, **kwargs):
            pass

    You can call this task this way:

        from django.utils import translation
        tasks.my_task.delay(any_optional_arguments, language=translation.get_language())
    '''
    def wrapper(*args, **kwargs):
        language = kwargs.pop('language', None)
        prev_language = translation.get_language()
        language and translation.activate(language)
        try:
            return func(*args, **kwargs)
        finally:
            translation.activate(prev_language)

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    return wraps(func)(wrapper)

class respect_to_language:
    '''
    Class for 'with' statement. It changes current language for all code only inside this statement.
    You can use it anywhere, for example, inside task methods this way:

        @task
        def my_task(language=None):
            with respect_to_language(language):
                pass
    '''
    language = None
    language_prev = None

    def __init__(self, language):
        self.language = language

    def __enter__(self):
        self.language_prev = translation.get_language()
        self.language and translation.activate(self.language)

    def __exit__(self, type, value, traceback):
        translation.activate(self.language_prev)