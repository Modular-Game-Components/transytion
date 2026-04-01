# Based on https://github.com/rxi/flux/blob/master/flux.lua
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
    return -math.cos(x * (math.pi * (1/2.0))) + 1
