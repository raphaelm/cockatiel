cockatiel
=========

[![Build Status](https://travis-ci.org/raphaelm/cockatiel.svg?branch=master)](https://travis-ci.org/raphaelm/cockatiel)
[![Documentation Status](https://readthedocs.org/projects/cockatiel/badge/?version=latest)](http://cockatiel.readthedocs.org/en/latest/?badge=latest)

**THIS IS HIGHLY EXPERIMENTAL, DON'T USE IT IN PRODUCTION (YET)**

cockatiel is a replicating file server for small-scale setups. It is intended
to be used e.g. for handling user-uploaded files to a web application
in a redundant way.

cockatiel doesn't try to be a CDN, but to implement the simplest
solution that fulfills our needs. Currently, cockatiel makes the following
assumptions. If those won't work for you, you should probably be looking
for a CDN-like solution.

Assumptions
-----------

* All files can and should be on all cockatiel servers, no sharding

* File names don't matter to you, we'll add the file's hashsum to the name

* Files get replicated asynchronously. If that fails, the request will
  be retried eventually.

* Files don't change (if they do, they get a new filename)

* Adding or removing nodes from the cluster requires manual intervention

* Files are small enough to be held in memory for a short period

Read more
---------

Please head to our [Documentation](https://cockatiel.readthedocs.org/en/latest/) for
more information on how to install, use and contribute!

There is a [Django storage backend](https://github.com/raphaelm/django-cockatiel)
available that uses cockatiel.