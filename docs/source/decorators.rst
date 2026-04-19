Decorators for Tweening
=======================

Often when thinking in game development terms, it can be tempting to think of game logic and then easing and tweens as an afterwards. Unfortunately, this can result in a lot of code restructuring. Transytion can help prevent major refactoring by utilizing Python decorators.

Consider the following scenario: You want a player to move and then say something. Ignoring animations, one might write:

.. code-block:: python

   def say_something():
       print("Hello!")

   say_something()

But if we follow the example above it is a little awkward to combine this with move:

.. code-block:: python

   def say_something():
       print("Hello!")

   move = Tween(..., callback=say_something)

   ...

transytion uses decorators to minimize cognitive load. The following is equivalent to the previous example:

.. code-block:: python

   move = Tween(...)
   @tween_then_call(move)
   def say_something():
       print("Hello!")

   say_something()
   ...

The ``@tween_then_call(tween)`` decorator delays function calls to execute after the supplied tween executes. Thus, we can focus on game logic first *then* decorate the logic to incorporate tweens.
