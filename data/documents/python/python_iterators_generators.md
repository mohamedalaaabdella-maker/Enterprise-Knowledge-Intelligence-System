# Python Iterators and Generators

Source: Python Documentation
URL: https://docs.python.org/3.14/tutorial/classes.html#iterators
Version: 3.14
License: PSF-2.0 (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Iterators

By now you have probably noticed that most container objects can be looped over using a `for` statement:

    for element in [1, 2, 3]:
        print(element)
    for element in (1, 2, 3):
        print(element)
    for key in {'one':1, 'two':2}:
        print(key)
    for char in "123":
        print(char)
    for line in open("myfile.txt"):
        print(line, end='')

This style of access is clear, concise, and convenient. The use of iterators pervades and unifies Python. Behind the scenes, the `for` statement calls `iter` on the container object. The function returns an iterator object that defines the method `__next__` which accesses elements in the container one at a time. When there are no more elements, `__next__` raises a `StopIteration` exception which tells the `for` loop to terminate. You can call the `__next__` method using the `next` built-in function; this example shows how it all works:

    >>> s = 'abc'
    >>> it = iter(s)
    >>> it
    <str_iterator object at 0x10c90e650>
    >>> next(it)
    'a'
    >>> next(it)
    'b'
    >>> next(it)
    'c'
    >>> next(it)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
        next(it)
    StopIteration

Having seen the mechanics behind the iterator protocol, it is easy to add iterator behavior to your classes. Define an `__iter__` method which returns an object with a `__next__` method. If the class defines `__next__`, then `__iter__` can just return `self`:

    class Reverse:
        """Iterator for looping over a sequence backwards."""
        def __init__(self, data):
            self.data = data
            self.index = len(data)

        def __iter__(self):
            return self

        def __next__(self):
            if self.index == 0:
                raise StopIteration
            self.index = self.index - 1
            return self.data[self.index]

    >>> rev = Reverse('spam')
    >>> iter(rev)
    <__main__.Reverse object at 0x00A1DB50>
    >>> for char in rev:
    ...     print(char)
    ...
    m
    a
    p
    s

## Generators

`Generators` are a simple and powerful tool for creating iterators. They are written like regular functions but use the `yield` statement whenever they want to return data. Each time `next` is called on it, the generator resumes where it left off (it remembers all the data values and which statement was last executed). An example shows that generators can be trivially easy to create:

    def reverse(data):
        for index in range(len(data)-1, -1, -1):
            yield data[index]

    >>> for char in reverse('golf'):
    ...     print(char)
    ...
    f
    l
    o
    g

Anything that can be done with generators can also be done with class-based iterators as described in the previous section. What makes generators so compact is that the `__iter__` and `__next__` methods are created automatically.

Another key feature is that the local variables and execution state are automatically saved between calls. This made the function easier to write and much more clear than an approach using instance variables like `self.index` and `self.data`.

In addition to automatic method creation and saving program state, when generators terminate, they automatically raise `StopIteration`. In combination, these features make it easy to create iterators with no more effort than writing a regular function.

## Generator Expressions

Some simple generators can be coded succinctly as expressions using a syntax similar to list comprehensions but with parentheses instead of square brackets. These expressions are designed for situations where the generator is used right away by an enclosing function. Generator expressions are more compact but less versatile than full generator definitions and tend to be more memory friendly than equivalent list comprehensions.

Examples:

    >>> sum(i*i for i in range(10))                 # sum of squares
    285

    >>> xvec = [10, 20, 30]
    >>> yvec = [7, 5, 3]
    >>> sum(x*y for x,y in zip(xvec, yvec))         # dot product
    260

    >>> unique_words = set(word for line in page  for word in line.split())

    >>> valedictorian = max((student.gpa, student.name) for student in graduates)

    >>> data = 'golf'
    >>> list(data[i] for i in range(len(data)-1, -1, -1))
    ['f', 'l', 'o', 'g']

## Generators in Depth (Functional Programming HOWTO)

Generators are a special class of functions that simplify the task of writing iterators. Regular functions compute a value and return it, but generators return an iterator that returns a stream of values.

You're doubtless familiar with how regular function calls work in Python or C. When you call a function, it gets a private namespace where its local variables are created. When the function reaches a `return` statement, the local variables are destroyed and the value is returned to the caller. A later call to the same function creates a new private namespace and a fresh set of local variables. But, what if the local variables weren't thrown away on exiting a function? What if you could later resume the function where it left off? This is what generators provide; they can be thought of as resumable functions.

Here's the simplest example of a generator function:

```python
>>> def generate_ints(N):
... for i in range(N):
... yield i
```

Any function containing a `yield` keyword is a generator function; this is detected by Python's `bytecode` compiler which compiles the function specially as a result.

When you call a generator function, it doesn't return a single value; instead it returns a generator object that supports the iterator protocol. On executing the `yield` expression, the generator outputs the value of `i`, similar to a `return` statement. The big difference between `yield` and a `return` statement is that on reaching a `yield` the generator's state of execution is suspended and local variables are preserved. On the next call to the generator's `__next__` method, the function will resume executing.

Here's a sample usage of the `generate_ints()` generator:

```python
>>> gen = generate_ints(3)
>>> gen  <generator object generate_ints at ...>
>>> next(gen) 0
>>> next(gen) 1
>>> next(gen) 2
>>> next(gen) Traceback (most recent call last): File "stdin", line 1, in <module> File "stdin", line 2, in generate_ints StopIteration
```

You could equally write `for i in generate_ints(5)`, or `a, b, c = generate_ints(3)`.

Inside a generator function, `return value` causes `StopIteration(value)` to be raised from the `__next__` method. Once this happens, or the bottom of the function is reached, the procession of values ends and the generator cannot yield any further values.

You could achieve the effect of generators manually by writing your own class and storing all the local variables of the generator as instance variables. For example, returning a list of integers could be done by setting `self.count` to 0, and having the `__next__` method increment `self.count` and return it. However, for a moderately complicated generator, writing a corresponding class can be much messier.

The test suite included with Python's library, `Lib/test/test_generators.py`, contains a number of more interesting examples. Here's one generator that implements an in-order traversal of a tree using generators recursively:

    # A recursive generator that generates Tree leaves in in-order.
    def inorder(t):
        if t:
            for x in inorder(t.left):
                yield x

            yield t.label

            for x in inorder(t.right):
                yield x

Two other examples in `test_generators.py` produce solutions for the N-Queens problem (placing N queens on an NxN chess board so that no queen threatens another) and the Knight's Tour (finding a route that takes a knight to every square of an NxN chessboard without visiting any square twice).
