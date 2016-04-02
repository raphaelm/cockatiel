cockatiel
=========

[![Build Status](https://travis-ci.org/raphaelm/cockatiel.svg?branch=master)](https://travis-ci.org/raphaelm/cockatiel)

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

* All files can and should be on all budgie servers, no sharding

* File names don't matter to you, we'll just name files by their hashsum

* Files get replicated asynchronously. If that fails, the request will
  be retried eventually.

* Files don't change (if they do, they get a new filename)

* Adding or removing nodes from the cluster requires manual intervention

Requirements
------------

* Python 3.4+

Installation
------------

TBD


Contributing
------------

* Check out our git repository

* Install the dependencies using ``pip install -r requirements.txt``. You'll
  need a fairly recent pip version and we recommend using virtual
  environments.

* You can run all the functional tests using ``py.test functional_tests/``