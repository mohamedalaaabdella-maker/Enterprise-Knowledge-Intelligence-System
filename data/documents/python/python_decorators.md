# Python Function Decorators

Source: Python Documentation
URL: https://docs.python.org/3.14/reference/compound_stmts.html#function-definitions
Version: 3.14
License: PSF-2.0 (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Decorator Syntax and Semantics

A function definition may be wrapped by one or more `decorator` expressions. Decorator expressions are evaluated when the function is defined, in the scope that contains the function definition. The result must be a callable, which is invoked with the function object as the only argument. The returned value is bound to the function name instead of the function object. Multiple decorators are applied in nested fashion. For example, the following code:

    @f1(arg)
    @f2
    def func(): pass

is roughly equivalent to:

    def func(): pass
    func = f1(arg)(f2(func))

except that the original function is not temporarily bound to the name `func`.

*Version note (3.9):* Functions may be decorated with any valid `assignment_expression`. Previously, the grammar was much more restrictive; see PEP 614 for details.

## Default Parameter Values in Function Definitions

When one or more `parameters` have the form *parameter* `=` *expression*, the function is said to have "default parameter values." For a parameter with a default value, the corresponding `argument` may be omitted from a call, in which case the parameter's default value is substituted. If a parameter has a default value, all following parameters up until the "`*`" must also have a default value --- this is a syntactic restriction that is not expressed by the grammar.

**Default parameter values are evaluated from left to right when the function definition is executed.** This means that the expression is evaluated once, when the function is defined, and that the same "pre-computed" value is used for each call. This is especially important to understand when a default parameter value is a mutable object, such as a list or a dictionary: if the function modifies the object (e.g. by appending an item to a list), the default parameter value is in effect modified. This is generally not what was intended. A way around this is to use `None` as the default, and explicitly test for it in the body of the function, for example:

    def whats_on_the_telly(penguin=None):
        if penguin is None:
            penguin = []
        penguin.append("property of the zoo")
        return penguin

## functools.wraps

wraps(wrapped, assigned=WRAPPER_ASSIGNMENTS, updated=WRAPPER_UPDATES)

This is a convenience function for invoking `update_wrapper` as a function decorator when defining a wrapper function. It is equivalent to `partial(update_wrapper, wrapped=wrapped, assigned=assigned, updated=updated)`. For example:

    >>> from functools import wraps
    >>> def my_decorator(f):
    ...     @wraps(f)
    ...     def wrapper(*args, **kwds):
    ...         print('Calling decorated function')
    ...         return f(*args, **kwds)
    ...     return wrapper
    ...
    >>> @my_decorator
    ... def example():
    ...     """Docstring"""
    ...     print('Called example function')
    ...
    >>> example()
    Calling decorated function
    Called example function
    >>> example.__name__
    'example'
    >>> example.__doc__
    'Docstring'

Without the use of this decorator factory, the name of the example function would have been `'wrapper'`, and the docstring of the original `example` would have been lost.

## functools.cache

cache(user_function)

Simple lightweight unbounded function cache. Sometimes called ["memoize"](https://en.wikipedia.org/wiki/Memoization).

Returns the same as `lru_cache(maxsize=None)`, creating a thin wrapper around a dictionary lookup for the function arguments. Because it never needs to evict old values, this is smaller and faster than `lru_cache` with a size limit.

For example:

    @cache
    def factorial(n):
        return n * factorial(n-1) if n else 1

    >>> factorial(10)   # no previously cached result, makes 11 recursive calls
    3628800
    >>> factorial(5)    # no new calls, just returns the cached result
    120
    >>> factorial(12)   # two new recursive calls, factorial(10) is cached
    479001600

The cache is threadsafe so that the wrapped function can be used in multiple threads. This means that the underlying data structure will remain coherent during concurrent updates.

It is possible for the wrapped function to be called more than once if another thread makes an additional call before the initial call has been completed and cached.

## functools.lru_cache

lru_cache(user_function) lru_cache(maxsize=128, typed=False)

Decorator to wrap a function with a memoizing callable that saves up to the *maxsize* most recent calls. It can save time when an expensive or I/O bound function is periodically called with the same arguments.

The cache is threadsafe so that the wrapped function can be used in multiple threads. This means that the underlying data structure will remain coherent during concurrent updates.

It is possible for the wrapped function to be called more than once if another thread makes an additional call before the initial call has been completed and cached.

Since a dictionary is used to cache results, the positional and keyword arguments to the function must be `hashable`.

Distinct argument patterns may be considered to be distinct calls with separate cache entries. For example, `f(a=1, b=2)` and `f(b=2, a=1)` differ in their keyword argument order and may have two separate cache entries.

If *user_function* is specified, it must be a callable. This allows the *lru_cache* decorator to be applied directly to a user function, leaving the *maxsize* at its default value of 128:

    @lru_cache
    def count_vowels(sentence):
        return sum(sentence.count(vowel) for vowel in 'AEIOUaeiou')

If *maxsize* is set to `None`, the LRU feature is disabled and the cache can grow without bound.

If *typed* is set to true, function arguments of different types will be cached separately. If *typed* is false, the implementation will usually regard them as equivalent calls and only cache a single result. (Some types such as *str* and *int* may be cached separately even when *typed* is false.)

Note, type specificity applies only to the function's immediate arguments rather than their contents. The scalar arguments, `Decimal(42)` and `Fraction(42)` are treated as distinct calls with distinct results. In contrast, the tuple arguments `('answer', Decimal(42))` and `('answer', Fraction(42))` are treated as equivalent.

The wrapped function is instrumented with a `cache_parameters` function that returns a new `dict` showing the values for *maxsize* and *typed*. This is for information purposes only. Mutating the values has no effect.

## functools.cached_property

cached_property(func)

Transform a method of a class into a property whose value is computed once and then cached as a normal attribute for the life of the instance. Similar to `property`, with the addition of caching. Useful for expensive computed properties of instances that are otherwise effectively immutable.

Example:

    class DataSet:

        def __init__(self, sequence_of_numbers):
            self._data = tuple(sequence_of_numbers)

        @cached_property
        def stdev(self):
            return statistics.stdev(self._data)

The mechanics of `cached_property` are somewhat different from `property`. A regular property blocks attribute writes unless a setter is defined. In contrast, a *cached_property* allows writes.

The *cached_property* decorator only runs on lookups and only when an attribute of the same name doesn't exist. When it does run, the *cached_property* writes to the attribute with the same name. Subsequent attribute reads and writes take precedence over the *cached_property* method and it works like a normal attribute.

The cached value can be cleared by deleting the attribute. This allows the *cached_property* method to run again.

The *cached_property* does not prevent a possible race condition in multi-threaded usage. The getter function could run more than once on the same instance, with the latest run setting the cached value. If the cached property is idempotent or otherwise not harmful to run more than once on an instance, this is fine. If synchronization is needed, implement the necessary locking inside the decorated getter function or around the cached property access.
