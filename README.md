# transytion (pre-alpha)

`transytion` is a utility library for easily creating and managinig tweens in game engines like Pygame. It is heavily inspired by [Flux](https://github.com/rxi/flux) and [HUMP.timer](https://hump.readthedocs.io/en/latest/timer.html) from the [Love2d](https://www.love2d.org/) community.

## What is a tween?

A tween takes a variable and gradually changes it from one value to another as time progresses. A player may move from one point to another over a time period for instance. Thus, at the heart of it, a tween must:

- Take a certain `duration` over which to change a variable.
- Take one or more variables to change (called the `targets`)
- Take values to gradually change them too.
- A function that describes the gradual change.

Furthermore, it is often to have convenient to have a way to indicate to the program that the tween has finished. To do so, you may supply a `callback` function to execute once the tween has finished terminating.

## How do I use it?

This library allows you to make tweens and compose them with other tweens that can be used a variety of cases. For instance, you can move objects, change their color, etc. The library operates on fields of objects. Let us see what that means with an example in [Pygame-ce](https://pyga.me/docs/index.html) (although the example can be adapted to other game libraries).

```python
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
```

This is a modification of the first example presented [here](https://pyga.me/docs/index.html). It is recommended you become familiar with that example, and then continue with this example. If you run the program, a red circle moves down the screen. What is going on?

```python
@dataclass
class Ball:
    x: float
    y: float
```

This is used to keep track of the location of the ball on the screen. Tweens operate on fields of objects, so by making a `Ball` object we may tween the `y` (or `x`) fields.

```python
# 1 second qudratic fall to center of screen.
fall = ty.Tween(1.0, # Duration of tween is 1 seconds.
                ball, # What object to mess with.
                {"y" : screen.get_height() / 2}, # Animate what to where.
                ease_func=quad) # How to animate it (defaults to linear)
```

This constructs our tween. It should be pointed out, by itself, the `Tween` object does not do anything until we tell it to run.

```python
ty.default_manager.add(fall) # Start the tween.
```

Once the tween is added to a `TweenManager` object, (such as `ty.default_manager`) the tween begins execution. You can make as many manager objects as you want, but you need at least one, and it is perfectly reasonable to use just one. That is why `transytion` includes a `default_manager` for ease of use.

Lastly, the `TweenManager` needs the time to update each tween it is managing. This is done by going to your game loop and adding the line

```python
ty.default_manager.update(dt)
```

## Making more complicated tweens with `chain`

If you perform

```python
ty.default_manager.add(t1)
ty.default_manager.add(t2)
```

`ty.default_manager` will run both tweens simultaneously. If we want to run `t1` to execute and then `t2` we may `chain` them together:

```python
t3 = chain([t1, t2])
ty.default_manager.add(t3)
```

Using `chain`, complicated tweens can be made from smaller tweens. See [this](https://github.com/thyrgle/transytion/blob/main/examples/chained_tween.py) for a complete example.

## A Brief Overview of the Library

The code for the `Tween` class roughly implements a (doubly) linked list (with a couple super powers!) that store `TweenNode` data. You can think of each `TweenNode` as being a fundamental building block for creating more complex `Tween` objects (but for convenience, the API allows you to just use the `Tween` class).

The `TweenManager` keeps a list of tweens and in a [slightly tricky `for` loop progresses through each tween.](https://github.com/thyrgle/transytion/blob/653b9f03412eb16d1af77447b69ba199343dc34e/src/transytion/__init__.py#L91)
