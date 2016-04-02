HTTP API
========

cockatiel exposes a HTTP API that you can use to store, retrieve
and delete files from its storage. The same API is being used by
cockatiel for the communication between different nodes.

API methods
-----------

.. http:get:: /(filename)

   Returns the file with the given filename.

   :resheader Content-Type: The content type of a file, determined
                            by its extension
   :status 200: if the file exists and can be read.
   :status 404: if the file does not exist
   :status 500: on any internal errors

.. http:put:: /(filename)

   Creates a new file with the given filename. You are not
   guaranteed that the file is actually created with the given name,
   you should expect to get a new name in the ``Location`` response
   header.

   :resheader Location: The relative or abosulte URL to the file
                            with the name that acutally has been used
                            when storing the file.
   :status 201: if the file did not exist on this server before
   :status 302: if the file already existed on this server previously
   :status 500: on any internal errors

.. http:delete:: /(filename)

   Deletes the file of the given name.

   :status 200: if the file could be deleted successfully
   :status 404: if the file did not exist
   :status 500: on any internal errors
