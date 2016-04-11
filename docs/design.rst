Design decisions
================

Cockatiel doesn't try to be a CDN, but to implement the simplest
solution that fulfills our needs. Currently, cockatiel makes a number
of assumptions that are outlined below. If those assumptions do not apply
to your needs, you should probably be looking for a CDN-like solution
or for a proper distributed file system or block device.

.. _assumptions:

Assumptions
-----------

**All files are on all servers.** Cockatiel currently does not implement any
kind of sharding and we do not plan to do so, so Cockatiel is designed for
file collections that can easily fit on a modern hard drive.

**File names will be (partly) auto-generated.** In order to avoid collisions,
cockatiel will insert a file's SHA1 checksum and the current timestamp
into the filename. Therefore, the file will not be stored exactly at the
location the client specified. Please note that this might disclose when the
file was created.

**Files get replicated asynchronously.** If your network connection is slow
or flaky, this can lead to a delay between a file being on one server and a
file being distributed across all servers.

**Files don't change.** It is not possible to change a file through cockatiel.
If you want to replace a file, just delete the old one and upload a new one
that will get a new name (due to the checksum that will be inserted into the
filename).

**Adding or removing nodes may require manual intervention.** There currently
is neither automatic service discovery nor cluster configuration management
during runtime.

**Files are being served by a different webserver.** Cockatiel does not
intend to be a high-performance web server. If your files get accessed a lot,
please use a proper web server like nginx and point it to the cockatiel's
storage directory.

Implementation
--------------

* cockatiel is a stand-alone service implemented in Python using ``asyncio``.

* The service exposes a very simple :ref:`http-api` that is used both for
  the communication between a client and the service as well as for the
  replication between the cockatiel nodes.

* Every operation gets inserted into a queue. This queue is persisted to a
  directory on the file system. An operation stays inside the queue as long
  as it has not been accepted by all neighbor servers.

* In order to resolve conflicts between creations and deletions, we keep a
  log of all files deleted recently and any node will not accept replications
  for a files in this log. Due to the time-based filenames, we can safely
  assume that a file won't be re-uploaded with the same name after it has
  been deleted.

Failure modes
-------------

cockatiel is currently designed to automatically cope with the following
events:

**Server downtime:** If one node of the cluster goes offline, the other
servers will queue up all operations and retry them periodically. The
retrial interval is currently configured to increase from twice a second
two once every 30 seconds if the server is down for a longer period.
Therefore, once the server returns, the other servers will start pushing
all changes within 30 seconds.

**Network corruption:** If a file arrives corrupted after a replication,
e.g. the calculated SHA1 sums of the sender and the receiver mismatch,
the operation will be aborted and retried.

**Network partition:** If you have three nodes A, B, and C, and the network
between A and C gets interrupted, an operation performed on A will still
be propagated to server C.

**Connection interruption:** Any operation stays queued for replication
as long as the receiving server did not acknowledge it. Therefore,
if an operation is interrupted, it will be retried.