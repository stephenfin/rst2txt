# -*- coding: utf-8 -*-
"""
    rst2txt.__main__
    ~~~~~~~~~~~~~~~~

    A minimal front end to the Docutils Publisher, producing plain text.

    :copyright: Copyright 2018, Stephen Finucane <stephen@that.guru>.
    :license: BSD, see LICENSE for details.
"""
import locale
locale.setlocale(locale.LC_ALL, '')  # noqa

from docutils.core import default_description
from docutils.core import publish_cmdline
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

from rst2txt.writer import Writer

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass


def main():
    description = ('Generates plain text documents from standalone '
                   'reStructuredText sources.  ' + default_description)

    publish_cmdline(writer=Writer(), writer_name='txt',
                    description=description)
