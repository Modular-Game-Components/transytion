from __future__ import annotations
from collections.abc import Callable
from itertools import pairwise
from dataclasses import dataclass
from typing import Any

from .ease_funcs import linear


class Tween:
    def __init__(self,
                 duration: float, 
                 obj: Any, 
                 targets: dict[(str, float)],
                 start: dict[(str, float)] | None = None,
                 ease_func: Callable[[float], float] = linear,
                 callback: Callable[[], None] = lambda: None):
        """Make a tween with one TweenNode contained in it."""
        tween = TweenNode(duration, obj, targets,
                          start, ease_func, callback)
        self._initial = tween
        self._last = tween
        self._cur = tween

    def reset(self):
        self._cur = self._initial


@dataclass
class TweenNode:
    duration: float
    obj: Any
    targets: dict[(str, float)] # String of the attributes you want to mutate!
    start: dict[(str, float)] | None = None
    ease_func: Callable[[float], float] = linear
    callback: Callable[[], None] = lambda: None
    _progress: float = 0.0
    _next_: TweenNode | None = None
    _prev_: TweenNode | None = None
    _paused: bool = False

    def __post_init__(self):
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
        if self.start is not None:
            for target, start in self.start:
                self._original.update(self.start)

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
            loc = (1 - p) * self._original[var] + p * self._destinations[var]
            setattr(self.obj, var, loc)


class TweenManager:
    _to_update: list[Tween]
    
    def __init__(self):
        self._to_update = []

    def add(self, tween: Tween):
        tween._cur.safe_reset_to_start()
        self._to_update.append(tween)

    def remove(self, tween: Tween):
        self._to_update.remove(tween)

    def update(self, dt):
        # Remove finished tweens.
        self._to_update = [x for x in self._to_update if x._cur is not None]
        # Must use range len pattern, since we must mutate the object.
        for i in range(len(self._to_update)):
            # However, most of the loop treats `_to_update` as immutable, so, 
            # for convenience, we refer to it as `tween_node`.
            tween_node = self._to_update[i]._cur
            # If it is paused, don't do anything.
            if tween_node._paused:
                continue
            if tween_node.progress < 1.0: # TweenNode in process.
                tween_node.progress += dt / tween_node.duration
            else: # TweenNode finished, move to the next.
                tween_node.callback()
                # Mut to next is here.
                self._to_update[i]._cur = tween_node._next_
                if self._to_update[i]._cur is not None:
                    # Determine whether to continue from current target's val
                    # or if the target val should be set to `start` for the
                    # next TweenNode.
                    self._to_update[i]._cur.safe_reset_to_start()
                # Otherwise, entire Tween has finished. (Will be removed in
                # next call to update.

    def pause(self, tween: Tween):
        tween._paused = True

    def resume(self, tween: Tween):
        tween._paused = False

    def pause_all(self):
        for tween in self._to_update:
            tween._paused = True

    def remove_all(self):
        self._to_update = []


default_manager = TweenManager()


def chain(tweens: list[Tween]) -> Tween:
    """Take a list of tweens and create a single tween that is equivalent to 
    each tween followed by the next."""
    initial = tweens[0]._initial
    last = tweens[-1]._last
    for t1, t2 in pairwise(tweens):
        t1._last._next_ = t2._initial
        t2._initial._prev_ = t1._last
        t1._last = last
        t2._last = last
        t1._initial = initial
        t2._initial = initial
    return tweens[0]
