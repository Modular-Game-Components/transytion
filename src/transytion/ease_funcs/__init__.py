# Based on https://github.com/rxi/flux/blob/master/flux.lua
from collections.abc import Callable
import math


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

def sine(x: float) -> float:
    """Sinusoidal tween."""
    return 1 - math.cos(x * math.pi / 2)


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
