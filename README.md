cockatiel
=========

[![Build Status](https://travis-ci.org/raphaelm/cockatiel.svg?branch=master)](https://travis-ci.org/raphaelm/cockatiel)
[![Documentation Status](https://readthedocs.org/projects/cockatiel/badge/?version=latest)](http://cockatiel.readthedocs.org/en/latest/?badge=latest)

**THIS IS HIGHLY EXPERIMENTAL, DON'T USE IT IN PRODUCTION (YET)**

Cockatiel is a replicating file server for small-scale setups. It is intended
to be used e.g. for handling user-uploaded files to a web application
in a redundant way.

Cockatiel doesn't try to be a CDN, but to implement the simplest
solution that fulfills our needs. Currently, cockatiel makes the following
assumptions. If those won't work for you, you should probably be looking
for a CDN-like solution.

Cockatiel makes some very strong assumption about your use case, be sure to
read them in our [Documentation](https://cockatiel.readthedocs.org/en/latest/design.html#assumptions)
before you decide to use cockatiel.

Read more
---------

Please head to our [Documentation](https://cockatiel.readthedocs.org/en/latest/) for
more information on how to install, use and contribute!

There is a [Django storage backend](https://github.com/raphaelm/django-cockatiel)
available that uses cockatiel.

Author
------

Raphael Michel <mail@raphaelmichel.de>