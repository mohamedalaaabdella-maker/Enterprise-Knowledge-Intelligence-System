# Python Context Managers and the with Statement

Source: Python Documentation
URL: https://docs.python.org/3.14/library/contextlib.html
Version: 3.14
License: PSF-2.0 (license of the original documentation; this file is an excerpt reformatted as Markdown)

## The with Statement

The `with` statement is used to wrap the execution of a block with methods defined by a context manager (see section With Statement Context Managers). This allows common `try`...`except`...`finally` usage patterns to be encapsulated for convenient reuse.

The execution of the `with` statement with one "item" proceeds as follows:

1.  The context expression (the expression given in the `with_item`) is evaluated to obtain a context manager.

2.  The context manager's `__enter__` is loaded for later use.

3.  The context manager's `__exit__` is loaded for later use.

4.  The context manager's `__enter__` method is invoked.

5.  If a target was included in the `with` statement, the return value from `__enter__` is assigned to it.

    Note

    The `with` statement guarantees that if the `__enter__` method returns without an error, then `__exit__` will always be called. Thus, if an error occurs during the assignment to the target list, it will be treated the same as an error occurring within the suite would be. See step 7 below.

6.  The suite is executed.

7.  The context manager's `__exit__` method is invoked. If an exception caused the suite to be exited, its type, value, and traceback are passed as arguments to `__exit__`. Otherwise, three `None` arguments are supplied.

    If the suite was exited due to an exception, and the return value from the `__exit__` method was false, the exception is reraised. If the return value was true, the exception is suppressed, and execution continues with the statement following the `with` statement.

    If the suite was exited for any reason other than an exception, the return value from `__exit__` is ignored, and execution proceeds at the normal location for the kind of exit that was taken.

The following code:

    with EXPRESSION as TARGET:
        SUITE

is semantically equivalent to:

    manager = (EXPRESSION)
    enter = manager.__enter__
    exit = manager.__exit__
    value = enter()
    hit_except = False

    try:
        TARGET = value
        SUITE
    except:
        hit_except = True
        if not exit(*sys.exc_info()):
            raise
    finally:
        if not hit_except:
            exit(None, None, None)

except that implicit `special method lookup` is used for `__enter__` and `__exit__`.

With more than one item, the context managers are processed as if multiple `with` statements were nested:

    with A() as a, B() as b:
        SUITE

is semantically equivalent to:

    with A() as a:
        with B() as b:
            SUITE

You can also write multi-item context managers in multiple lines if the items are surrounded by parentheses. For example:

    with (
        A() as a,
        B() as b,
    ):
        SUITE

*Version note (3.1):* Support for multiple context expressions.

*Version note (3.10):* Support for using grouping parentheses to break the statement in multiple lines.

PEP 343 - The "with" statement
The specification, background, and examples for the Python `with` statement.

## Context Manager Protocol: __enter__ and __exit__

A `context manager` is an object that defines the runtime context to be established when executing a `with` statement. The context manager handles the entry into, and the exit from, the desired runtime context for the execution of the block of code. Context managers are normally invoked using the `with` statement (described in section `with`), but can also be used by directly invoking their methods.

Typical uses of context managers include saving and restoring various kinds of global state, locking and unlocking resources, closing opened files, etc.

For more information on context managers, see the Context Manager Types section of the standard library reference. The `object` class itself does not provide the context manager methods.

object.__enter__(self)

Enter the runtime context related to this object. The `with` statement will bind this method's return value to the target(s) specified in the `as` clause of the statement, if any.

object.__exit__(self, exc_type, exc_value, traceback)

Exit the runtime context related to this object. The parameters describe the exception that caused the context to be exited. If the context was exited without an exception, all three arguments will be `None`.

If an exception is supplied, and the method wishes to suppress the exception (i.e., prevent it from being propagated), it should return a true value. Otherwise, the exception will be processed normally upon exit from this method.

Note that `__exit__` methods should not reraise the passed-in exception; this is the caller's responsibility.

PEP 343 - The "with" statement
The specification, background, and examples for the Python `with` statement.

## contextlib.contextmanager

contextmanager

This function is a `decorator` that can be used to define a factory function for `with` statement context managers, without needing to create a class or separate `__enter__` and `__exit__` methods.

While many objects natively support use in with statements, sometimes a resource needs to be managed that isn't a context manager in its own right, and doesn't implement a `close()` method for use with `contextlib.closing`.

An abstract example would be the following to ensure correct resource management:

    from contextlib import contextmanager

    @contextmanager
    def managed_resource(*args, **kwds):
        # Code to acquire resource, e.g.:
        resource = acquire_resource(*args, **kwds)
        try:
            yield resource
        finally:
            # Code to release resource, e.g.:
            release_resource(resource)

The function can then be used like this:

    >>> with managed_resource(timeout=3600) as resource:
    ...     # Resource is released at the end of this block,
    ...     # even if code in the block raises an exception

The function being decorated must return a `generator`-iterator when called. This iterator must yield exactly one value, which will be bound to the targets in the `with` statement's `as` clause, if any.

At the point where the generator yields, the block nested in the `with` statement is executed. The generator is then resumed after the block is exited. If an unhandled exception occurs in the block, it is reraised inside the generator at the point where the yield occurred. Thus, you can use a `try`...`except`...`finally` statement to trap the error (if any), or ensure that some cleanup takes place. If an exception is trapped merely in order to log it or to perform some action (rather than to suppress it entirely), the generator must reraise that exception. Otherwise the generator context manager will indicate to the `with` statement that the exception has been handled, and execution will resume with the statement immediately following the `with` statement.

`contextmanager` uses `ContextDecorator` so the context managers it creates can be used as decorators as well as in `with` statements. When used as a decorator, a new generator instance is implicitly created on each function call (this allows the otherwise "one-shot" context managers created by `contextmanager` to meet the requirement that context managers support multiple invocations in order to be used as decorators).

*Version note (3.2):* Use of `ContextDecorator`.

## contextlib.closing

closing(thing)

Return a context manager that closes *thing* upon completion of the block. This is basically equivalent to:

    from contextlib import contextmanager

    @contextmanager
    def closing(thing):
        try:
            yield thing
        finally:
            thing.close()

And lets you write code like this:

    from contextlib import closing
    from urllib.request import urlopen

    with closing(urlopen('https://www.python.org')) as page:
        for line in page:
            print(line)

without needing to explicitly close `page`. Even if an error occurs, `page.close()` will be called when the `with` block is exited.

Note

Most types managing resources support the `context manager` protocol, which closes *thing* on leaving the `with` statement. As such, `closing` is most useful for third party types that don't support context managers. This example is purely for illustration purposes, as `urlopen` would normally be used in a context manager.

## contextlib.suppress

suppress(\*exceptions)

Return a context manager that suppresses any of the specified exceptions if they occur in the body of a `with` statement and then resumes execution with the first statement following the end of the `with` statement.

As with any other mechanism that completely suppresses exceptions, this context manager should be used only to cover very specific errors where silently continuing with program execution is known to be the right thing to do.

For example:

    from contextlib import suppress

    with suppress(FileNotFoundError):
        os.remove('somefile.tmp')

    with suppress(FileNotFoundError):
        os.remove('someotherfile.tmp')

This code is equivalent to:

    try:
        os.remove('somefile.tmp')
    except FileNotFoundError:
        pass

    try:
        os.remove('someotherfile.tmp')
    except FileNotFoundError:
        pass

This context manager is `reentrant`.

If the code within the `with` block raises a `BaseExceptionGroup`, suppressed exceptions are removed from the group. Any exceptions of the group which are not suppressed are re-raised in a new group which is created using the original group's `derive` method.

*Version note (3.12):* `suppress` now supports suppressing exceptions raised as part of a `BaseExceptionGroup`.
