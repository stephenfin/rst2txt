# -*- coding: utf-8 -*-
"""
Test for text writer.
"""
from __future__ import print_function

import tempfile
import textwrap

from docutils.core import publish_string

import rst2txt


def assert_serialized(source, expected_output, settings=None):
    source = textwrap.dedent(source)
    expected_output = textwrap.dedent(expected_output)

    actual_output = publish_string(source=source, writer=rst2txt.Writer(),
                                   settings_overrides=settings)

    assert expected_output == actual_output.decode('utf-8')


def test_basic():
    source = """\
    this is a paragraph.

    ----------

    this is another paragraph.

    a section
    ---------

    foo.

    .. code-block:: python

       print('Some code')

    a subsection
    ~~~~~~~~~~~~

    foo
      A special word

    bar
      A less special word
    """
    output = """\
    this is a paragraph.

    ======================================================================

    this is another paragraph.


    a section
    *********

    foo.

       print('Some code')


    a subsection
    ============

    foo
       A special word

    bar
       A less special word
    """

    assert_serialized(source, output)


def test_eol_windows():
    source = """\
    this is a test.
    """

    output = """\
    this is a test.
    """.replace('\n', '\r\n')

    assert_serialized(source, output, settings={'newlines': 'windows'})


def test_eol_linux():
    source = """\
    this is a test.
    """

    output = """\
    this is a test.
    """.replace('\r\n', '\n')

    assert_serialized(source, output, settings={'newlines': 'linux'})


def test_admonitions():
    source = """\
    .. important:: Really important information

    .. warning:: Less important information

    .. tip::

       General information but really descriptive in order to force line
       wrapping at some point.
    """
    output = """\
    Important: Really important information

    Warning: Less important information

    Tip: General information but really descriptive in order to force
      line wrapping at some point.
    """

    assert_serialized(source, output)


def test_images_disabled():
    source = """\
    this is an image.

    .. image:: test.png
       :alt: A test image
    """
    output = """\
    this is an image.
    """

    assert_serialized(source, output, settings={'add_images': False})


def test_images_enabled():
    source = """\
    this is an image.

    .. image:: test.png
       :alt: A test image
    """
    output = """\
    this is an image.

    [image: A test image][image]
    """

    assert_serialized(source, output, settings={'add_images': True})


def test_rubric():
    source = """\
    .. rubric:: Something important
    """
    output = """\
    -[ Something important ]-
    """

    assert_serialized(source, output)


def test_tables_table():
    source = """\
    .. table:: Truth table for "not"
       :class: custom
       :name:  tab:truth.not

       =====  =====
         A    not A
       =====  =====
       False  True
       True   False
       =====  =====
    """
    output = """\

    Truth table for "not"
    ^^^^^^^^^^^^^^^^^^^^^

    +-------+-------+
    | A     | not A |
    |=======|=======|
    | False | True  |
    +-------+-------+
    | True  | False |
    +-------+-------+
    """

    assert_serialized(source, output)


def test_tables_list_table():
    source = """\
    .. list-table:: list table with integral header
       :widths: 10 20 30
       :header-rows: 1
       :stub-columns: 1

       * - Treat
         - Quantity
         - Description
       * - Albatross
         - 2.99
         - On a stick!
       * - Crunchy Frog
         - 1.49
         - If we took the bones out, it wouldn\'t be
           crunchy, now would it?
       * - Gannet Ripple
         - 1.99
         - On a stick!
    """
    output = """\

    list table with integral header
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    +------------+----------------------+--------------------------------+
    | Treat      | Quantity             | Description                    |
    |============|======================|================================|
    | Albatross  | 2.99                 | On a stick!                    |
    +------------+----------------------+--------------------------------+
    | Crunchy    | 1.49                 | If we took the bones out, it   |
    | Frog       |                      | wouldn't be crunchy, now would |
    |            |                      | it?                            |
    +------------+----------------------+--------------------------------+
    | Gannet     | 1.99                 | On a stick!                    |
    | Ripple     |                      |                                |
    +------------+----------------------+--------------------------------+
    """

    assert_serialized(source, output)


def test_tables_csv_table():
    source = """\
    .. csv-table:: inline table with integral header
       :widths: 10, 20, 30
       :header-rows: 1
       :stub-columns: 1

       "Treat", "Quantity", "Description"
       "Albatross", 2.99, "On a stick!"
       "Crunchy Frog", 1.49, "If we took the bones out, it wouldn\'t be
       crunchy, now would it?"
       "Gannet Ripple", 1.99, "On a stick!"
    """
    output = """\

    inline table with integral header
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    +------------+----------------------+--------------------------------+
    | Treat      | Quantity             | Description                    |
    |============|======================|================================|
    | Albatross  | 2.99                 | On a stick!                    |
    +------------+----------------------+--------------------------------+
    | Crunchy    | 1.49                 | If we took the bones out, it   |
    | Frog       |                      | wouldn't be crunchy, now would |
    |            |                      | it?                            |
    +------------+----------------------+--------------------------------+
    | Gannet     | 1.99                 | On a stick!                    |
    | Ripple     |                      |                                |
    +------------+----------------------+--------------------------------+
    """

    assert_serialized(source, output)


def test_include():
    with tempfile.NamedTemporaryFile(delete=False) as include_file:
        include_file.write(b'This is a test.\n')

    source = """
    .. include:: {}
    """.format(include_file.name)
    output = """\
    This is a test.
    """

    assert_serialized(source, output)
