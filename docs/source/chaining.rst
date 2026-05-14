Chaining Tweens Together
========================

-----------------------------------
Bounce *then* Role: A First Attempt
-----------------------------------

Suppose we want to create something like:

.. image:: (TODO)

That is, we want the ball to bounce *then* role to the right off the screen.

We can re-use the previous example ``fall`` tween. That is:

.. code-block:: python

   fall = ty.Tween(1.0, ball,
                   {"y" : screen.get_height() / 2},
                   ease_func=bounce)

Then we need a tween for rolling. So, we must now modify the ``x`` attribute so it is off screen. Consider:

.. code-block:: python

   roll = ty.Tween(1.0, ball,
                   {"x" : screen.get_width() + ball.r},
                   ease_func=quad)

One might be tempted to do:

.. code-block:: python
   ty.default_manager.add(fall)
   ty.default_manager.add(roll)

But that does not quite work. Observe:

.. image:: (TODO)

---------------------------------
What Went Wrong? (And How to Fix)
---------------------------------

For more complicated movements, we may need to tween multiple values at once. In fact, this is more likely to happen than sequentially running tween after tween. Thus, simply adding the tweens to a manager will run them *concurrently*. Fortunately, it is not too hard to fix. We will use the ``transytion.chain`` function to force a sequence of tweens to run in order. Replace:

.. code-block:: python
   ty.default_manager.add(fall)
   ty.default_manager.add(roll)

with

.. code-block:: python
   ty.default_manager.add(ty.chain([fall, roll]))

The ``transytion.chain``, in this case, will return a new tween that runs the ``fall`` tween and *then* the ``roll`` tween.

For the sake of completeness, here is the entire example (it should look similar to the previous example!):

.. code-block:: python

   import transytion as ty
   from dataclasses import dataclass
   from transytion.ease_funcs import bounce, quad
   import pygame


   pygame.init()
   screen = pygame.display.set_mode((1280, 720))
   clock = pygame.time.Clock()
   running = True
   dt = 0

   @dataclass
   class Ball:
       x: float
       y: float
       r: float

   ball = Ball(screen.get_width() / 2.0, 0.0 - 40.0, 40.0)

   fall = ty.Tween(1.0, ball,
                {"y" : screen.get_height() / 2},
                  ease_func=bounce)

   roll = ty.Tween(1.0, ball,
                   {"x" : screen.get_width() + ball.r},
                   ease_func=quad)

   ty.default_manager.add(ty.chain([fall, roll]))

   while running:
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               running = False

       ty.default_manager.update(dt)
 
       screen.fill((0,0,0))
       pygame.draw.circle(screen, "red", (ball.x, ball.y), 40)

       pygame.display.flip()
       dt = clock.tick(60) / 1000

   pygame.quit()
