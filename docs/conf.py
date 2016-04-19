#!/usr/bin/env python3

import sys
import os

import sphinx_readable_theme

sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = 'typecaster'
copyright = '2016, Neil Bedi'
author = 'Neil Bedi'

version = '0.1.0'
release = '0.1.0'

language = None

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'

todo_include_todos = False

html_theme = 'readable'

html_theme_path = [sphinx_readable_theme.get_html_theme_path()]

html_static_path = ['_static']

htmlhelp_basename = 'typecasterdoc'

latex_elements = {}

latex_documents = [
    (master_doc, 'typecaster.tex', 'typecaster Documentation',
     'Neil Bedi', 'manual'),
]

man_pages = [
    (master_doc, 'typecaster', 'typecaster Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'typecaster', 'typecaster Documentation',
     author, 'typecaster', 'One line description of project.',
     'Miscellaneous'),
]

intersphinx_mapping = {'https://docs.python.org/': None}

autodoc_member_order = 'bysource'
