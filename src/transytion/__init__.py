from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass
from copy import copy
from typing import Any

from .ease_funcs import linear


class Tween:
    """A list of TweenNodes with some organizational skills."""
    def __init__(self,
                 duration: float, 
                 obj: Any, 
                 targets: dict[str, float],
                 start: dict[(str, float)] | None = None,
                 ease_func: Callable[[float], float] = linear,
                 before_execution: Callable[[], None] = lambda: None,
                 callback: Callable[[], None] = lambda: None,
                 on_pause: Callable[[], None] = lambda: None,
                 on_remove: Callable[[], None] = lambda: None,
                 args: tuple[Any, ...] = tuple(),
                 repeat_count: int = 1
                 ):
        """Make a tween with one TweenNode contained in it."""
        node = TweenNode(duration, obj, targets,
                         start, ease_func, callback, args)
        self.current = 0
        self.nodes = [node]
        node.start()
        self._before_execution = before_execution
        self._callback = callback
        self._on_pause = on_pause
        self._on_remove = on_remove
        self._args = args
        self._repeat_count = repeat_count
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
        self.nodes[-1].args = args

    @property
    def callback(self):
        """Get the *final* callback."""
        return self._callback

    @callback.setter
    def callback(self, callback: Callable[[]]):
        """Set the *final* callback."""
        self.nodes[-1].callback = callback
        self._callback = callback

    def pause(self):
        """Pause a tween. Tells the manager of this tween to put it in the
        paused tweens list."""
        self._on_pause()
        self._manager.paused_tweens.append(self)
        self._manager.active_tweens.remove(self)

    def resume(self):
        """Resume a tween. If the tween was paused, it is now put in the active
        tween list and resumed by it's manager."""
        self._manager.active_tweens.append(self)
        self._manager.paused_tweens.remove(self)

    @property
    def finished(self):
        """Determine if a tween has finished going *forward* or *backward*."""
        return self.current < 0 \
            or self.current >= len(self.nodes) * self._repeat_count

    def update(self, dt) -> None:
        """Updates the current TweenNode and transitions to the next
        TweenNode if the current one has finished updating."""
        cur = self.nodes[self.current % len(self.nodes)]
        nxt = self.nodes[(self.current + 1) % len(self.nodes)]
        cur.update(dt)
        if cur.progress >= 1:
            self.current += 1
            cur.finish()
            nxt.start()
            nxt.progress = 0
        # The whole tween finished, remove it from the _manager.
        if self.finished:
            self._manager.remove(self)
            self._manager = None

    def reset(self):
        """Restarts a tween from the beginning."""
        # Reset the individual nodes.
        for node in self.nodes:
            self.progress = 0
        # Then reset to beginning.
        self.current = 0

    def then(self, other):
        self.nodes.extend(other.nodes)


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
    start_vals: dict[str, float] | None = None
    ease_func: Callable[[float], float] = linear
    callback: Callable[[], None] = lambda: None
    args: tuple[Any, ...] = tuple()
    _progress: float = 0.0

    def start(self):
        """Must also have the original and resulting position to actually tween
        between those values."""
        self._original = {}
        self._destinations = {}
        # Just use what ever value the obj currently has.
        for target, dest in self.targets.items():
            self._original[target] = getattr(self.obj, target)
            self._destinations[target] = dest

    def safe_reset_to_start(self):
        """If start position is specified (not None), make sure values start
        from the start. Otherwise, start from where they currently are."""
        if self.start_vals is not None:
            for target, start in self.start_vals:
                self._original.update(self.start_vals)

    def finish(self):
        self.callback(*self.args)

    def update(self, dt):
        if self.progress < 1.0:
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


class TweenManager:
    """Keeps track of updating tweens in an update loop."""
    def __init__(self):
        self.active_tweens = []
        self.paused_tweens = []

    def add(self, tween: Tween):
        tween.reset()
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
    start = copy(tweens[0])
    for tween in tweens[1:]:
        start.then(tween)
    return start

def repeat(tween: Tween, count=float("inf")) -> Tween:
    """Repeats `count` times. (Defaults to indefinitely, that is float("inf")
    """
    new_tween = copy(tween)
    new_tween._repeat_count = count
    return new_tween
