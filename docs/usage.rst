Using cockatiel
===============

Requirements
------------

* cockatiel requires Python 3.4 or newer

* cockatiel has only been tested in Linux so far

Installation
------------

Installing cockatiel is really straightforward. We recommend that you set it up
inside a `virtual environment`_ in order to isolate its dependencies from other
python projects that you might use. Inside the Python 3 virtual environment you
can then just run::

   $ pip install cockatiel

to obtain the latest release.

.. warning:: Before using cockatiel for your project, please make sure that
             you read and understood the :ref:`assumptions` that cockatiel
             makes about your requirements.

Command-line options
--------------------

Cockatiel is currently configured via command-line parameters.

.. argparse::
   :ref: cockatiel.config.get_parser
   :prog: python3 -m cockatiel


Running cockatiel as a service
------------------------------

To automatically run cockatiel at system startup, you can register it as a
system service.

TBD systemd example

Adding new nodes to the cluster
-------------------------------

If you're system is growing and you'd like to add a new node to the cluster,
you'll need to go through the following steps in the given order:

#. Set up and start cockatiel on the new server, including all existing servers in
   its cluster configuration.

#. Add the URL of the new server to the cluster configuration on all other nodes,
   then restart those nodes.

#. Manually copy over the complete storage directory from one of the existing nodes
   to your new node, e.g. using ``rsync``.

Using cockatiel for a Django application
----------------------------------------

We have a Django storage backend for cockatiel available at `django-cockatiel`_.

.. _django-cockatiel: https://github.com/raphaelm/django-cockatiel
.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/
