..  Titling
    ##++::==~~--''``

Object serialisation
====================

The :py:class:`Assembly <turberfield.utils.assembly.Assembly>` class
provides a means of saving your objects to JSON format. They are
saved with type information so that you can load them back again as
Python objects.

.. autoclass:: turberfield.utils.assembly.Assembly
   :members: register, dumps, dump, loads
   :member-order: bysource
