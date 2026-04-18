What is a Tween?
================


A tween takes a variable and gradually changes it from one value to another as time progresses. A player may move from one point to another over a time period for instance. Thus, at the heart of it, a tween must:

* Take a certain ``duration`` over which to change a variable.
* Take one or more variables to change (called the ``targets``)
* Take values to gradually change them too.
* A function that describes the gradual change.

Furthermore, it is often to have convenient to have a way to indicate to the program that the tween has finished. To do so, you may supply a ``callback`` function to execute once the tween has finished terminating.
