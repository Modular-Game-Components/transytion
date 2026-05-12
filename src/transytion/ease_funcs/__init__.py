# Based on https://github.com/rxi/flux/blob/master/flux.lua
# and https://easings.net/
from collections.abc import Callable
import math


def sine(x: float) -> float:
    """Sinusoidal tween."""
    return 1 - math.cos(x * math.pi / 2)

def linear(x: float) -> float:
    """Linear tween that returns the thing itself."""
    return x

def quad(x: float) -> float:
    """Quadratic tween, returns the square of itself."""
    return x ** 2

def cubic(x: float) -> float:
    """Cubic tween, returns the cube of itself."""
    return x ** 3

def quart(x: float) -> float:
    """Quartic tween, returns itself raised to the fourth power."""
    return x ** 4

def quint(x: float) -> float:
    """Quintic tween, returns itself raised to the fifth power."""
    return x ** 5

def expo(x: float) -> float:
    """Exponential tween, returns 2^(10x - 10)."""
    if x == 0:
        return 0
    return 2 ** (10 * x - 10)

def circ(x: float) -> float:
    """Returns a circular tween. See https://easings.net/#easeInCirc"""
    return 1 - math.sqrt(1 - x ** 2)

def back(x: float) -> float:
    """Returns 'back' tween. See: https://easings.net/#easeInBack"""
    c1 = 1.70158
    c2 = c1 + 1
    return c2 * (x ** 3) - c1 * (x ** 2)

def elastic(x: float) -> float:
    """Returns elastic tween. See https://easings.net/#easeInElastic"""
    c = (2 * math.pi) / 3
    if x == 0:
        return 0
    elif x == 1:
        return 1
    return -(2 ** (10 * x - 10)) * math.sin((x * 10 - 10.75) * c)

def bounce(x: float) -> float:
    """Performs bound (out) tween. See https://easings.net/#easeOutBounce"""
    n = 7.5625
    d = 2.75

    if x < 1.0 / d:
        return n * x * x
    elif x < 2.0 / d:
        x -= 1.5 / d
        return n * x * x + 0.75
    elif x < 2.5 / d:
        x -= 2.25 / d
        return n * x * x + 0.9375
    else:
        x -= 2.625 / d
        return n * x * x + 0.984375

# Common in-out functions (in is just the original function).
# See https://hump.readthedocs.io/en/latest/timer.html#tweening-methods for
# more information.
# Supply an easeing function *as* an argument to either `out` or `inout`.

def inout(f: Callable[[float], float]) -> Callable[[float], float]:
    """Doubles the speed of an easing function ``f``. Plays the easing function
    then plays the reverse of ``f`` for the second half of the tween."""
    def g(x: float) -> float:
        x *= 2
        if x < 1:
            return 1/2 * f(x)
        else:
            x = 2 - x
            return 1/2 * (1 - f(x)) + 1/2
    return g

def out(f: Callable[[float], float]) -> Callable[[float], float]:
    """Reverses the easing function."""
    def g(x: float) -> float:
        return 1 - f(x)
    return g
