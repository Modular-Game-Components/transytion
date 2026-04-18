Chaining Tweens Together
========================

If you perform

.. code-block:: python

   ty.default_manager.add(t1)
   ty.default_manager.add(t2)

``ty.default_manager`` will run both tweens simultaneously. If we want to run ``t1`` to execute and then ``t2`` we may ``chain`` them together:

.. code-block:: python

   t3 = chain([t1, t2])
   ty.default_manager.add(t3)

Using ``chain``, complicated tweens can be made from smaller tweens.
