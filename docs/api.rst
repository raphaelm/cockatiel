.. _http-api:

HTTP API
========

Cockatiel exposes a HTTP API that you can use to store, retrieve
and delete files from its storage. The same API is being used by
cockatiel for the communication between different nodes.

API methods
-----------

.. http:get:: /(filename)

   Returns the file with the given filename.

   :reqheader If-None-Match: A value that you obtained from the
                             ``ETag`` header of a response that you
                             still have in your cache.
   :resheader Content-Type: The content type of a file, determined
                            by its extension
   :resheader ETag: A hash value specific to this file. You can
                    specify this in the ``If-None-Match`` request
                    header for cache validation.
   :resheader Cache-Control: Cache control instructions, normally
                             telling you that you can cache this for
                             at least a year.
   :resheader X-Content-SHA1: The SHA1 hash of the transmitted file
   :status 200: if the file exists and can be read
   :status 304: if you provided ``If-None-Match``
   :status 404: if the file does not exist
   :status 500: on any internal errors

.. http:put:: /(filename)

   Creates a new file with the given filename. You are not
   guaranteed that the file is actually created with the given name,
   you should expect to get a new name in the ``Location`` response
   header.

   :reqheader X-Content-SHA1: The SHA1 hash of the transmitted file (optional)
   :resheader Location: The relative or abosulte URL to the file
                        with the name that acutally has been used
                        when storing the file.
   :status 201: if the file did not exist on this server before
   :status 302: if the file already existed on this server previously
   :status 400: if you specified a SHA1 hash and it does not match the
                hash calculated on the server
   :status 408: if data is coming in to slow
   :status 500: on any internal errors

.. http:delete:: /(filename)

   Deletes the file of the given name.

   :status 200: if the file could be deleted successfully
   :status 404: if the file did not exist
   :status 500: on any internal errors

.. http:head:: /(filename)

   Returns the meta data for the file with the given filename. This
   behaves exactly the same as ``GET``, it just does not return the
   file's content.

   :reqheader If-None-Match: A value that you obtained from the
                             ``ETag`` header of a response that you
                             still have in your cache.
   :resheader Content-Type: The content type of a file, determined
                            by its extension
   :resheader ETag: A hash value specific to this file. You can
                    specify this in the ``If-None-Match`` request
                    header for cache validation.
   :resheader Cache-Control: Cache control instructions, normally
                             telling you that you can cache this for
                             at least a year.
   :resheader X-Content-SHA1: The SHA1 hash of the file
   :status 200: if the file exists and can be read
   :status 304: if you provided ``If-None-Match``
   :status 404: if the file does not exist
   :status 500: on any internal errors

.. http:get:: /_status

   Returns status information on this node. This currently includes a
   dictionary that contains one dictonary for every neighbor node. This
   inner dictionary contains the current length of the replication queue,
   i.e. the number of operations known to this node that have not yet been
   sent to the respective other node.

   Example response::

        {
            "queues": {
                "http://localhost:9001": {
                    "length": 4
                }
            }
        }

   :status 200: in any known case