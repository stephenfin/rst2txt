rst2txt
=======

reStructuredText is pretty-damn consumable in its raw form, but extensive use
of directives and roles can hamper things or leave the document incomplete in
its raw form (cough, ``.. include``, cough).

*rst2txt* allows you to work around this by evaluating the reStructuredText
source and stripping it of most of its formatting. The end result is a document
that's more readable and has elements that don't make sense in a plain text
document, such as images, stripped.

*rst2txt* is based on the ``sphinx.writer.text.TextWriter`` writer used by
Sphinx's `TextBuilder
<https://www.sphinx-doc.org/en/1.8/usage/builders/index.html#sphinx.builders.text.TextBuilder>`__
but with the Sphinx-specific features stripped out.

Installation
------------

*rst2txt* is available on PyPI. To install, run:

.. code-block:: shell

   $ pip install --user rst2txt

Usage
-----

Most users will want just the ``rst2txt`` application:

.. code-block:: shell

   $ rst2txt README.rst

It is also possible to call this programmatically though. This can be useful
for things like consuming README files:

.. code-block:: python

   from docutils.core import publish_file
   import rst2txt

   with open('README.rst', 'r') as source:
       publish_file(source=source, destination_path='README.txt',
                    writer=rst2txt.Writer())
