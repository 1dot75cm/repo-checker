repo-checker
------------

.. image:: https://img.shields.io/badge/license-MIT-brightgreen.svg
  :target: LICENSE
.. image:: https://img.shields.io/badge/python-2.7-green.svg
.. image:: https://img.shields.io/badge/python-3.5-green.svg

.. image:: https://files.gitter.im/1dot75cm/KWdU/2016-12-30-23-20-24-_____.png
  :target: https://pypi.python.org/pypi/repo-checker/

repo-checker is a graphical user interface version checker for open source projects. It works with Python 2.7/3.x and PyQt 4/5.

It uses the requests package to get the release page, and uses XPath rules to match time. And then, convert it to timestamp and compare them. Finally, it tell you that some projects has been updated.
