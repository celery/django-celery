'''
>>> from djcelery.decorators import respect_to_language
>>> from django.utils import translation
>>> language = translation.get_language()
>>> language != 'ru'
True
>>> with respect_to_language('ru'):
...     translation.get_language()
'ru'
>>> language == translation.get_language()
True
'''