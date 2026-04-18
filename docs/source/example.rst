Example Usage (Pygame)
======================

This library allows you to make tweens and compose them with other tweens that can be used a variety of cases. For instance, you can move objects, change their color, etc. The library operates on fields of objects. Let us see what that means with an example in `Pygame-ce <https://pyga.me/docs/>`_ (although the example can be adapted to other game libraries).

.. code-block:: python

   import transytion as ty
   from dataclasses import dataclass
   from transytion.ease_funcs import quad
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

   ball = Ball(screen.get_width() / 2.0, 0.0)

   # 1 second qudratic fall to center of screen.
   fall = ty.Tween(1.0, # Duration of tween is 1 seconds.
                   ball, # What object to mess with.
                   {"y" : screen.get_height() / 2}, # Animate what to where.
                   ease_func=quad) # How to animate it (defaults to linear)

   ty.default_manager.add(fall) # Start the tween.

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

This is a modification of the first example presented `here <https://pyga.me/docs/>`_. It is recommended you become familiar with that example, and then continue with this example. If you run the program, a red circle moves down the screen. 
What is going on?
-----------------

.. codeblock:: python

   @dataclass
   class Ball:
       x: float
       y: float

This is used to keep track of the location of the ball on the screen. Tweens operate on attributes of objects, so by making a ``Ball`` object we may tween the ``y`` (or ``x``) attributes.

.. codeblock:: python

   # 1 second qudratic fall to center of screen.
   fall = ty.Tween(1.0, # Duration of tween is 1 seconds.
                   ball, # What object to mess with.
                   {"y" : screen.get_height() / 2}, # Animate what to where.
                   ease_func=quad) # How to animate it (defaults to linear)

This constructs our tween. It should be pointed out, by itself, the ``Tween`` object does not do anything until we tell it to run.

.. codeblock:: python

   ty.default_manager.add(fall) # Start the tween.

Once the tween is added to a ``TweenManager`` object, (such as ``ty.default_manager``) the tween begins execution. You can make as many manager objects as you want, but you need at least one, and it is perfectly reasonable to use just one. That is why transytion includes a ``default_manager`` for ease of use.

Lastly, the ``TweenManager`` needs the time to update each tween it is managing. This is done by going to your game loop and adding the line

.. codeblock:: python

   ty.default_manager.update(dt)
