# Configuration file for the Sphinx documentation builder.

# -- Project information
import os
import re
import sys

import django

sys.path.insert(0, os.path.abspath("../.."))

import epsg_cache  # noqa

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(os.path.abspath(
        '../..'), package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]",
                     init_py, re.MULTILINE).group(1)


VERSION = get_version("epsg_cache")

project = 'django-epsg-cache'
copyright = '2023, MrMap community'
author = 'MrMap community'

release = VERSION
version = VERSION

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
