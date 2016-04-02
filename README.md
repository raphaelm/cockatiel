django-parrot
=============

**THIS IS HIGHLY EXPERIMENTAL, DON'T USE IT IN PRODUCTION (YET)**

django-parrot is a media file storage backend for Django that is useful 
if your Django application is running across multiple servers. It is 
meant to be used by sites that want to replicate their Django application
on multiple servers.

django-parrot doesn't try to be a CDN, but to implement the simplest 
solution that fulfills our needs. Currently, django-parrot makes the 
following assumptions. If those won't work for you, you should probably 
be looking for a CDN-like solution.

Assumptions
-----------

* The files will be on the same servers that run your Django application

* All files can and should be on all application servers

* File names don't matter and can be changed e.g. the hash of the file

* Files get replicated asynchronously. If that fails, the request will
  be retried eventually.

* Files don't change (if they do, they get a new filename)


