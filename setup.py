#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
import platform

try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES

import djcelery as distmeta

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
src_dir = "djcelery"


def osx_install_data(install_data):

    def finalize_options(self):
        self.set_undefined_options("install", ("install_lib", "install_dir"))
        install_data.finalize_options(self)


def fullsplit(path, result=None):
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

SKIP_EXTENSIONS = [".pyc", ".pyo", ".swp", ".swo"]


def is_unwanted_file(filename):
    for skip_ext in SKIP_EXTENSIONS:
        if filename.endswith(skip_ext):
            return True
    return False

for dirpath, dirnames, filenames in os.walk(src_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith("."):
            del dirnames[i]
    for filename in filenames:
        if filename.endswith(".py"):
            packages.append('.'.join(fullsplit(dirpath)))
        elif is_unwanted_file(filename):
            pass
        else:
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in
                filenames]])


class RunTests(Command):
    description = "Run the django test suite from the tests dir."
    user_options = []
    extra_env = {}

    def run(self):
        for env_name, env_value in self.extra_env.items():
            os.environ[env_name] = str(env_value)

        this_dir = os.getcwd()
        testproj_dir = os.path.join(this_dir, "tests")
        os.chdir(testproj_dir)
        sys.path.append(testproj_dir)
        from django.core.management import execute_manager
        os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get(
                        "DJANGO_SETTINGS_MODULE", "settings")
        settings_file = os.environ["DJANGO_SETTINGS_MODULE"]
        settings_mod = __import__(settings_file, {}, {}, [''])
        execute_manager(settings_mod, argv=[
            __file__, "test"])
        os.chdir(this_dir)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class QuickRunTests(RunTests):
    extra_env = dict(SKIP_RLIMITS=1, QUICKTEST=1)


if os.path.exists("README.rst"):
    long_description = codecs.open("README.rst", "r", "utf-8").read()
else:
    long_description = "See http://github.com/ask/django-celery"


setup(
    name='django-celery',
    version=distmeta.__version__,
    description=distmeta.__doc__,
    author=distmeta.__author__,
    author_email=distmeta.__contact__,
    url=distmeta.__homepage__,
    platforms=["any"],
    license="BSD",
    packages=packages,
    data_files=data_files,
    scripts=["bin/djcelerymon"],
    zip_safe=False,
    install_requires=[
        "django-picklefield",
        "celery>=2.1.1",
    ],
    cmdclass={"test": RunTests, "quicktest": QuickRunTests},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Communications",
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": ["djcelerymon = djcelery.mon:main"]
    },
    long_description=long_description,
)
