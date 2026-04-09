# Based on https://github.com/rxi/flux/blob/master/flux.lua
from collections.abc import Callable
import math


def linear(x: float) -> float:
    """ Linear tween that returns the thing itself."""
    return x

def quad(x: float) -> float:
    return x ** 2

def cubic(x: float) -> float:
    return x ** 3

def quart(x: float) -> float:
    return x ** 4

def quint(x: float) -> float:
    return x ** 5

def sine(x: float) -> float:
    return 1 - math.cos(x * math.pi / 2)


# Common in-out functions (in is just the original function).
# See https://hump.readthedocs.io/en/latest/timer.html#tweening-methods for
# more information.

def inout(f: Callable[[float], float]) -> Callable[[float], float]:
    def g(x: float) -> float:
        x *= 2
        if x < 1:
            return 1/2 * f(x)
        else:
            x = 2 - x
            return 1/2 * (1 - f(x)) + 1/2
    return g

def out(f: Callable[[float], float]) -> Callable[[float], float]:
    def g(x: float) -> float:
        return 1 - f(x)
    return g
