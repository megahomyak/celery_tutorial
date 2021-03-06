import sys
import webbrowser

import markdown
from celery import group, chain

from tasks import add, sum_task

SYNOPSIS = f"""
For this `synopsis.py` file to be runnable, you need to start a Celery worker
using the following command: `celery -A worker worker -l INFO` (`-A` is an
alias for `--app`, whilst `-l` is an alias for `--loglevel`).


# Promises (or "tasks")
A promise can be created using the `.task()` decorator, taken from a `Celery`
object:

    app = Celery(...)

    @app.task
    def add(x, y):
        return x + y

    @app.task
    def sum_task(numbers):
        return sum(numbers)

Then, you can invoke the promise directly: `{add(2, 2) = }`. This will execute
the promise in the current thread, not using the worker. If you want to invoke
a function using the running worker, you would write: `{add.delay(2, 2) = }`.
This is just a star-argument alias of another method:
`{add.apply_async((2, 2)) = }`. `.apply_async()` has way more capabilities,
and you may find it useful in some situations, so check it out just in case.

As you may have noticed, `add.delay(2, 2)` returned something strange. This
object - instance of `AsyncResult` - is used to asynchronously wait for the
results and gather them. You can get the results by invoking `.get()` on the
`AsyncResult`: `{add.delay(2, 2).get() = }`. You can specify a `timeout=` for
this method if you want. The unary negation operator (`~`) is used as a
shorthand for `.delay().get()`, what you will see further.


# Signatures
Signatures are basically `partial`s (from the `functools` module) combined
with `PromiseProxy` (from the `celery` module): `{add.s(1, 2) = }`.

`PromiseProxy.s()` is just an alias for `PromiseProxy.signature()` with
starred arguments and fewer capabilities, just like with `.delay()` and
`.apply_async()`.

Signatures can be invoked just as regular `@task`-marked functions:
`{add.s(1, 2).delay().get() = }`. Also, here I can show you the first example
of a unary negation used as a shorthand for `.delay().get()`:
{~add.s(1, 2) = }. This form of writing will be used where possible from now
on.

Also, as already mentioned, they can be used like `partial`s:
`{add.s(1).delay(2).get() = }`.
**When invoking a signature, new arguments will be prepended, not appended.**

Signatures are of the `celery.canvas.Signature` type.


# Data structures

These are more ways of processing data than data structures, actually. Each of
them takes an `Iterable` as an argument (i.e. any object that has the
`__iter__` method), but I use tuples here for convenience. The rules of
signatures also apply on data structures: a simple call does not use the
worker process and does everything locally (in the current process),
`.apply_async()` uses the worker process, `~` can be used as a shorthand for
`.delay().get()`, and you can use these new objects as `partial`s. Well,
except `.map()`, `.starmap()` or `.chunks()` - they cannot be used as a
`partial`. And also except `chord`s - they do not support local execution, and
also you cannot use message queues as their backend.

## Groups
Groups are the ordered collections of signatures:
`{group(add.s(1, 2), add.s(3, 4)) = }`.

If a group is invoked, it behaves like an invocation of a list of signatures:
`{~group(add.s(1, 2), add.s(3, 4)) = }`.

They can also be used like `partial`s:
`{group((add.s(1), add.s(2))).delay(10).get() = }`.

## Chains
`chain`s make it possible to invoke a promise when another returns:
`{~chain(add.s(1, 2) | add.s(4)) = }`. They can also be written in
this way: `{~(add.s(1, 2) | add.s(4)) = }`.
Again, `partial`s: `{(add.s(2) | add.s(1)).delay(3).get() = }`.

## Chords
`chord`s are used to send the results of several promises to one promise.
Like that: `chord(add.s(i, i) for i in range(10))(sum_task.s()).get()`.
Sadly, I wasn't able to test this code, because the price of it is setting
up PostgreSQL or some other database as a backend, and I don't want to spend
my time on it now. But you can test it yourself! Just set up PostgreSQL (or
any other database, in-memory databases will also work) as a backend for
Celery, add braces around the expression above and re-compile the synopsis by
running the `synopsis.py` script!

## Maps
`.map()` can only be used on functions that take one argument. `.map()` takes
an iterable of arguments and returns a list of results for corresponding
arguments. `.map()` returns an instance of the `celery.canvas.xmap` class and
can be invoked using negation: `{~sum_task.map([[1, 2], [3, 4]]) = }` (notice
that `sum_task` is being called now).

## Starmaps
Same as `.map()`s, but can supply more than one argument:
`{~add.starmap([[1, 2], [3, 4]]) = }`
(notice that `add` is being called now).

## Chunks
`.chunks()` is like a `.starmap()`, but divided to chunks of the specified
length: `{~add.chunks([(1, 2), (3, 4)], 10) = }`.
""".strip()

if sys.argv[1] == "--markdown":
    with open("synopsis.md", "w", encoding="utf-8") as f:
        f.write(SYNOPSIS)
else:
    with open("synopsis.html", "w", encoding="utf-8") as f:
        f.write(markdown.markdown(SYNOPSIS))
    webbrowser.open_new("synopsis.html")
