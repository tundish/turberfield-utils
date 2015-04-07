..  Titling
    ##++::==~~--''``

Agent-oriented programming
==========================

A Turberfield application is made up of cohesive programs called
`Controllers`. Each controller contains specialised objects which
run on their own as autonomous agents.

When an agent has to share the data it creates, it's known as an
`Expert`. In Turberfield, experts:

    * operate autonomously within an event loop
    * publish certain attributes to other experts within the same
      controller
    * publish certain attributes to other controllers via RSON_
    * listen on a queue for messages from another expert
    * listen on a queue for messages from another controller
    * can be configured with global settings like file paths
      and host names

Turberfield provides the :py:mod:`expert <turberfield.utils.expert>`
module to standardise this pattern. Subclasses of
:py:class:`Expert <turberfield.utils.expert.Expert>` inherit these
behaviours.

Using an Expert subclass
~~~~~~~~~~~~~~~~~~~~~~~~

Turberfield defines a three-stage process for setting up Expert objects
and running them. There are particular conventions around:

* Configuration_
* Instantiation_
* Invocation_

.. automodule:: turberfield.utils.expert

Subclassing Expert
~~~~~~~~~~~~~~~~~~

.. autoclass:: turberfield.utils.expert.Expert
   :members: options, watch, Attribute
   :member-order: bysource

.. _RSON: https://code.google.com/p/rson/
