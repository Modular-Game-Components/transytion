from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass
from copy import copy
from typing import Any
import itertools

from .ease_funcs import linear


class Tween:
    """A list of TweenNodes with some organizational skills."""
    def __init__(self,
                 duration: float = 0.0, 
                 obj: Any = None,
                 targets: dict[str, float] = {},
                 children: [Tween | TweenNode] = [],
                 start_val: dict[(str, float)] | None = None,
                 ease_func: Callable[[float], float] = linear,
                 before_execution: Callable[[], None] = lambda: None,
                 callback: Callable[[], None] = lambda: None,
                 on_pause: Callable[[], None] = lambda: None,
                 on_remove: Callable[[], None] = lambda: None,
                 args: tuple[Any, ...] = tuple(),
                 ):
        """Make a tween either with TweenNode params or a collection of Tweens."""
        if len(children) == 0:
            node = TweenNode(duration, obj, targets,
                             ease_func, callback, args)
            self.children = [node]
            self._iter_children = iter(self.children)
            self.duration = duration
        else:
            duration = 0
            for tween in children:
                duration += tween.duration
            self.duration = duration
            self.children = children
            self._iter_children = iter(children)
        self.cur = next(self._iter_children)
        self.cur.start()
        self._before_execution = before_execution
        self._callback = callback
        self._on_pause = on_pause
        self._on_remove = on_remove
        self._args = args
        self.finished = False
        # This will be set when a manager adds this tween.
        self._manager = None

    @property
    def args(self):
        """Get the args for the *final* callback."""
        return self._args

    @args.setter
    def args(self, args: tuple[Any, ...]):
        """Set the args for the *final* callback."""
        self._args = args

    @property
    def callback(self):
        """Get the *final* callback."""
        return self._callback

    @callback.setter
    def callback(self, callback: Callable[[], None]):
        """Set the *final* callback."""
        self._callback = callback

    def pause(self):
        """Pause a tween. Tells the manager of this tween to put it in the
        paused tweens list."""
        assert self._manager is not None, "Not added to a manager yet!"
        self._on_pause()
        self._manager.paused_tweens.append(self)
        self._manager.active_tweens.remove(self)

    def resume(self):
        """Resume a tween. If the tween was paused, it is now put in the active
        tween list and resumed by it's manager."""
        assert self._manager is not None, "Not added to a manager yet!"
        self._manager.active_tweens.append(self)
        self._manager.paused_tweens.remove(self)

    def start(self):
        """Start a tween from the beginning."""
        # Start the current node.
        self.cur.start()

    def update(self, dt) -> None:
        """Updates the current TweenNode and transitions to the next
        TweenNode if the current one has finished updating."""
        if self.finished and self._manager is not None:
            self._manager.remove(self)
            self._manager = None

        if self.cur.finished:
            try:
                self.cur = next(self._iter_children)
                self.cur.soft_reset()
                self.cur.start()
            except StopIteration:
                self.finished = True
                return
        self.cur.update(dt)

    def soft_reset(self):
        for tween in self.children:
            tween.soft_reset()
        self.finished = False
        self._iter_children = iter(self.children)
        self.cur = next(self._iter_children)

    def reset(self):
        """Restarts a tween from the beginning."""
        # Reset the individual tweens.
        for tween in self.children:
            tween.reset()
        # No longer have this tween be finished.
        self.finished = False
        # Restart the children iterator to be at the beginning.
        self._iter_children = iter(self.children)
        self.cur = next(self._iter_children)

# Some useful Tween specializations.

class Delay(Tween):
    """Does not do anything but waits some time."""
    def __init__(self, duration: float):
        super().__init__(duration, None, {})


@dataclass
class TweenNode:
    """Fundamental building block for Tweens."""
    duration: float
    obj: Any
    targets: dict[str, float] # String of the attributes you want to mutate!
    ease_func: Callable[[float], float] = linear
    callback: Callable[[], None] = lambda: None
    args: tuple[Any, ...] = tuple()
    _progress: float = 0.0

    def start(self):
        """Must also have the original and resulting position to actually tween
        between those values.
        NOTE: Instead of using __post__init__, we internally call start when
        needed. This makes chaining tweens significantly easier."""
        self._original = {}
        self._destinations = {}
        # Just use what ever value the obj currently has.
        for target, dest in self.targets.items():
            self._original[target] = getattr(self.obj, target)
            self._destinations[target] = dest
        self.soft_reset()

    def finish(self):
        self.callback()

    @property
    def finished(self):
        return self.progress >= 1.0

    def update(self, dt: float):
        self.progress += dt / self.duration

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value: float):
        """Setter for progress, must also update the targeted variables when
        progress is incremented."""
        self._progress = value
        for var in self.targets:
            p = self.ease_func(self._progress)
            orig = float(self._original[var])
            dest = float(self._destinations[var])
            loc = (1.0 - p) * orig + p * dest
            setattr(self.obj, var, loc)

    def reset(self):
        self.progress = 0.0

    def soft_reset(self):
        self._progress = 0.0


class TweenManager:
    """Keeps track of updating tweens in an update loop."""
    def __init__(self):
        self.active_tweens: list = []
        self.paused_tweens: list = []

    def add(self, tween: Tween):
        tween._manager = self
        self.active_tweens.append(tween)

    def remove(self, tween: Tween):
        # Note: This does not pause a tween. It *removes* it.
        tween._on_remove()
        self.active_tweens.remove(tween)

    def update(self, dt):
        for tween in self.active_tweens:
            tween.update(dt)

    def pause_all(self):
        for tween in self.active_tweens:
            tween._on_pause()
            tween.pause()

    def resume_all(self):
        for tween in self.paused_tweens:
            tween.resume()

    def remove_all(self):
        self.active_tweens = []
        self.paused_tweens = []


default_manager = TweenManager()


def tweenify(tween):
    """Makes a function when called return a tween that executes the
    decorated function for the tween's callback."""
    def decorator(func):
        def wrapper(*args):
            twn_cpy = copy(tween)
            twn_cpy._last.args = args
            twn_cpy._last.callback = func
            return twn_cpy
        return wrapper
    return decorator

def tween_then_call(tween: Tween, manager: TweenManager=default_manager):
    """Intended to be used as a decorator. Given a function f, f(args) now 
    executes the tween *then* calls the function. Similar to tweenify, but
    intended to be used by being added to a particular tween manager, and,
    by default, the default manager. This is largely a convenience decorator
    for tweenify.
    
    NOTE: f(args) followed by f(args) will not block the second call. Two 
    tweens will be added and both will do a double execution of f.
    NOTE: Because of Python limitations, cannot return value."""
    def decorator(func):
        def wrapper(*args):
            twn_cpy = copy(tween)
            twn_cpy.args = args
            twn_cpy.callback = func
            manager.add(twn_cpy)
        return wrapper
    return decorator

def call_then_tween(tween, manager=default_manager):
    """Intended to be used as a decorator. Given a function f, f(args) now 
    executes and then starts the tween.
    
    NOTE: f(args) followed by f(args) will not block the second call. Two 
    tweens will be added and both will do a double execution of f."""
    def decorator(func):
        def wrapper(*args):
            result = func(*args)
            twn_cpy = copy(tween)
            manager.add(twn_cpy)
            return result
        return wrapper
    return decorator

def chain(tweens: list[Tween]) -> Tween:
    """Take a list of tweens and create a single tween that is equivalent to 
    each tween followed by the next."""
    return Tween(children=tweens)

def repeat(tween: Tween, count=None) -> Tween:
    """Repeats `count` times. (Defaults to indefinitely = None)
    """
    if count is None:
        tween.children = itertools.cycle(tween.children)
        tween._iter_children = iter(tween.children)
        next(tween._iter_children) # Skip the first already done!
    else:
        tween.children = tween.children * count
        tween._iter_children = iter(tween.children)
        next(tween._iter_children) # Skip the first already done!
    return tween

