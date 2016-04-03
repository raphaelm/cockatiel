Contribution guide
==================

You are interesting in contributing to Cockatiel? That is awesome! If
you run into any problems with the steps below, please do not hesitate
to ask!

If you're new to contributing to open source software, don't be afraid
of doing so. We'll happily review your code and give you constructive and
friendly feedback on your changes.

Development setup
-----------------

First of all, make sure that you have Python 3.4 installed. We highly
recommend that you use a `virtual environment`_ for all of the following,
to keep this project's dependencies isolated from other Python projects
you might use or work on.

To get startet, first of all clone our git repository::

    $ git clone git@github.com:raphaelm/cockatiel.git
    $ cd cockatiel/

The second step is to make sure you have a recent version of pip and all
our requirements::

    $ pip install -U pip
    $ pip install -Ur requirements.txt

There is no third step :)

Running the software
--------------------

Running the cockatiel server is as easy as executing::

    $ python3 -m cockatiel

within the root directory of the repository.

Running the test suite
----------------------

Cockatiel's tests are split up into two parts. The unit tests are testing
single, isolated components of the codebase, the functional tests are
performing end-to-end tests of the API and they run tests on whole simulated
cluster setups. Therefore, the unit tests tend to run really fast while
running the functional tests might take a longer period of time. You can
run them with the following commands::

    $ py.test unit_tests
    $ py.test functional_tests

While working on the project, it may come useful to run only part of the test
suite. You can either specify a specific test file or even filter by the name
of the test::

    $ py.test unit_tests/test_queue.py
    $ py.test functional_tests/test_queue.py -kdelete

Building the documentation
--------------------------

To build the documentation as HTML files, you need to issue the following
commands::

    $ cd docs/
    $ make html

You can then point your browser to  ``<repo-path>/docs/_build/html/index.html``.

Sending a patch
---------------

If you improved cockatiel in any way, we'd be very happy if you contribute it
back to the main code base! The easiest way to do so is to `create a pull request`_
on our `GitHub repository`_.

Before you do so, please `squash all your changes`_ into one single commit. Please
use the test suite (see above) to check whether your changes break any existing
features. Please also run the following command to check for any code style
issues::

    $ flake8 cockatiel unit_tests functional_tests

We automatically run the tests and the code style check on every pull request on
Travis CI and we won't accept any pull requets without all tests passing.

If you add a new feature, please include appropriate documentation into your patch.
If you fix a bug, please include a regression test, i.e. a test that fails without
your changes and passes after applying your changes.

.. note:: If the tests fail on the Travis CI server but succeed on your local
          machine most of the time, don't panic. Due to the nature of some of the
          functional tests, they are not completely deterministic.

.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _create a pull request: https://help.github.com/articles/creating-a-pull-request/
.. _GitHub repository: https://github.com/raphaelm/cockatiel
.. _squash all your changes: https://davidwalsh.name/squash-commits-git