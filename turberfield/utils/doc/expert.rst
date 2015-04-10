..  Titling
    ##++::==~~--''``

Agent-oriented programming
==========================

A Turberfield application is made up of cohesive programs called
`Controllers`. Each controller contains specialised objects which
run on their own as autonomous agents.

When an agent has to share the data it creates, it's known as an
`Expert`. In Turberfield, experts:

    * can be configured with global settings like file paths
      and host names
    * listen on a queue for messages from another expert
    * listen on a queue for messages from another controller
    * operate autonomously within an event loop
    * publish certain attributes to other experts within the same
      controller
    * publish certain attributes to other controllers via RSON_

Turberfield provides the :py:mod:`expert <turberfield.utils.expert>`
module to standardise this pattern. Subclasses of
:py:class:`Expert <turberfield.utils.expert.Expert>` inherit these
behaviours.

Using an Expert subclass
~~~~~~~~~~~~~~~~~~~~~~~~

Turberfield defines a four-stage process for setting up Expert objects,
running them, and checking their results. There are conventions for each
of these interactions:

* Configuration_, where the class helps you build options for
  your new object.
* Instantiation_, where you connect the object to its inputs.
* Invocation_, which is compatible with the `asyncio event loop`_.
* Inspection_, the mechanism whereby your code can see the outputs
  of Experts in operation.

.. automodule:: turberfield.utils.expert

Subclassing Expert
~~~~~~~~~~~~~~~~~~

.. autoclass:: turberfield.utils.expert.Expert
   :members: options, __init__, watch, __call__, declare
   :member-order: bysource

.. _RSON: https://code.google.com/p/rson/
.. _asyncio event loop: https://docs.python.org/3/library/asyncio-eventloop.html
