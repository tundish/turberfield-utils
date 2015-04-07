..  Titling
    ##++::==~~--''``

Interprocess queues
===================

Turberfield provides a :py:mod:`pipes <turberfield.utils.pipes>` module
for interprocess communication. Your programs can send and receive
messages consisting of simple Python objects.

.. automodule:: turberfield.utils.pipes

.. autoclass:: turberfield.utils.pipes.SimplePipeQueue
   :members: pipequeue, put_nowait, get, close
   :member-order: bysource

.. autoclass:: turberfield.utils.pipes.PipeQueue
   :members: put, get

