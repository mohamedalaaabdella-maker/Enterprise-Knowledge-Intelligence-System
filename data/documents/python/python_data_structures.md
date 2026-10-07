# Python Data Structures

Source: Python Documentation
URL: https://docs.python.org/3.14/tutorial/datastructures.html
Version: 3.14
License: PSF-2.0 (license of the original documentation; this file is an excerpt reformatted as Markdown)

## More on Lists

The `list` data type has some more methods. Here are all of the methods of list objects:

list.append(value, /)

Add an item to the end of the list. Similar to `a[len(a):] = [x]`.

list.extend(iterable, /)

Extend the list by appending all the items from the iterable. Similar to `a[len(a):] = iterable`.

list.insert(index, value, /)

Insert an item at a given position. The first argument is the index of the element before which to insert, so `a.insert(0, x)` inserts at the front of the list, and `a.insert(len(a), x)` is equivalent to `a.append(x)`.

list.remove(value, /)

Remove the first item from the list whose value is equal to *value*. It raises a `ValueError` if there is no such item.

list.pop(index=-1, /)

Remove the item at the given position in the list, and return it. If no index is specified, `a.pop()` removes and returns the last item in the list. It raises an `IndexError` if the list is empty or the index is outside the list range.

list.clear()

Remove all items from the list. Similar to `del a[:]`.

list.index(value[, start[, stop]])

Return zero-based index of the first occurrence of *value* in the list. Raises a `ValueError` if there is no such item.

The optional arguments *start* and *end* are interpreted as in the slice notation and are used to limit the search to a particular subsequence of the list. The returned index is computed relative to the beginning of the full sequence rather than the *start* argument.

list.count(value, /)

Return the number of times *value* appears in the list.

list.sort(\*, key=None, reverse=False)

Sort the items of the list in place (the arguments can be used for sort customization, see `sorted` for their explanation).

list.reverse()

Reverse the elements of the list in place.

list.copy()

Return a shallow copy of the list. Similar to `a[:]`.

An example that uses most of the list methods:

    >>> fruits = ['orange', 'apple', 'pear', 'banana', 'kiwi', 'apple', 'banana']
    >>> fruits.count('apple')
    2
    >>> fruits.count('tangerine')
    0
    >>> fruits.index('banana')
    3
    >>> fruits.index('banana', 4)  # Find next banana starting at position 4
    6
    >>> fruits.reverse()
    >>> fruits
    ['banana', 'apple', 'kiwi', 'banana', 'pear', 'apple', 'orange']
    >>> fruits.append('grape')
    >>> fruits
    ['banana', 'apple', 'kiwi', 'banana', 'pear', 'apple', 'orange', 'grape']
    >>> fruits.sort()
    >>> fruits
    ['apple', 'apple', 'banana', 'banana', 'grape', 'kiwi', 'orange', 'pear']
    >>> fruits.pop()
    'pear'

You might have noticed that methods like `insert`, `remove` or `sort` that only modify the list have no return value printed -- they return the default `None`. This is a design principle for all mutable data structures in Python.

Another thing you might notice is that not all data can be sorted or compared. For instance, `[None, 'hello', 10]` doesn't sort because integers can't be compared to strings and `None` can't be compared to other types. Also, there are some types that don't have a defined ordering relation. For example, `3+4j < 5+7j` isn't a valid comparison.

### Using Lists as Stacks

The list methods make it very easy to use a list as a stack, where the last element added is the first element retrieved ("last-in, first-out"). To add an item to the top of the stack, use `append`. To retrieve an item from the top of the stack, use `pop` without an explicit index. For example:

    >>> stack = [3, 4, 5]
    >>> stack.append(6)
    >>> stack.append(7)
    >>> stack
    [3, 4, 5, 6, 7]
    >>> stack.pop()
    7
    >>> stack
    [3, 4, 5, 6]
    >>> stack.pop()
    6
    >>> stack.pop()
    5
    >>> stack
    [3, 4]

### Using Lists as Queues

It is also possible to use a list as a queue, where the first element added is the first element retrieved ("first-in, first-out"); however, lists are not efficient for this purpose. While appends and pops from the end of list are fast, doing inserts or pops from the beginning of a list is slow (because all of the other elements have to be shifted by one). See the Time Complexity page for more information.

## Tuples and Sequences

We saw that lists and strings have many common properties, such as indexing and slicing operations. They are two examples of *sequence* data types (see Sequence Types). Since Python is an evolving language, other sequence data types may be added. There is also another standard sequence data type: the *tuple*.

A tuple consists of a number of values separated by commas, for instance:

    >>> t = 12345, 54321, 'hello!'
    >>> t[0]
    12345
    >>> t
    (12345, 54321, 'hello!')
    >>> # Tuples may be nested:
    >>> u = t, (1, 2, 3, 4, 5)
    >>> u
    ((12345, 54321, 'hello!'), (1, 2, 3, 4, 5))
    >>> # Tuples are immutable:
    >>> t[0] = 88888
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: 'tuple' object does not support item assignment
    >>> # but they can contain mutable objects:
    >>> v = ([1, 2, 3], [3, 2, 1])
    >>> v
    ([1, 2, 3], [3, 2, 1])

As you see, on output tuples are always enclosed in parentheses, so that nested tuples are interpreted correctly; they may be input with or without surrounding parentheses, although often parentheses are necessary anyway (if the tuple is part of a larger expression). It is not possible to assign to the individual items of a tuple, however it is possible to create tuples which contain mutable objects, such as lists.

## Sets

Python also includes a data type for `sets`. A set is an unordered collection with no duplicate elements. Basic uses include membership testing and eliminating duplicate entries. Set objects also support mathematical operations like union, intersection, difference, and symmetric difference.

Curly braces or the `set` function can be used to create sets. Note: to create an empty set you have to use `set()`, not `{}`; the latter creates an empty dictionary, a data structure that we discuss in the next section.

Because sets are unordered, iterating over them or printing them can produce the elements in a different order than you expect.

Here is a brief demonstration:

    >>> basket = {'apple', 'orange', 'apple', 'pear', 'orange', 'banana'}
    >>> print(basket)                      # show that duplicates have been removed
    {'orange', 'banana', 'pear', 'apple'}
    >>> 'orange' in basket                 # fast membership testing
    True
    >>> 'crabgrass' in basket
    False

    >>> # Demonstrate set operations on unique letters from two words
    >>>
    >>> a = set('abracadabra')
    >>> b = set('alacazam')
    >>> a                                  # unique letters in a
    {'a', 'r', 'b', 'c', 'd'}
    >>> a - b                              # letters in a but not in b
    {'r', 'd', 'b'}
    >>> a | b                              # letters in a or b or both
    {'a', 'c', 'r', 'd', 'b', 'm', 'z', 'l'}
    >>> a & b                              # letters in both a and b
    {'a', 'c'}
    >>> a ^ b                              # letters in a or b but not both
    {'r', 'd', 'b', 'm', 'z', 'l'}

Similarly to `list comprehensions`, set comprehensions are also supported:

    >>> a = {x for x in 'abracadabra' if x not in 'abc'}
    >>> a
    {'r', 'd'}

## Dictionaries

Another useful data type built into Python is the *dictionary* (see Mapping Types). Dictionaries are sometimes found in other languages as "associative memories" or "associative arrays". Unlike sequences, which are indexed by a range of numbers, dictionaries are indexed by *keys*, which can be any immutable type; strings and numbers can always be keys. Tuples can be used as keys if they contain only strings, numbers, or tuples; if a tuple contains any mutable object either directly or indirectly, it cannot be used as a key. You can't use lists as keys, since lists can be modified in place using index assignments, slice assignments, or methods like `append` and `extend`.

It is best to think of a dictionary as a set of *key: value* pairs, with the requirement that the keys are unique (within one dictionary). A pair of braces creates an empty dictionary: `{}`. Placing a comma-separated list of key:value pairs within the braces adds initial key:value pairs to the dictionary; this is also the way dictionaries are written on output.

The main operations on a dictionary are storing a value with some key and extracting the value given the key. It is also possible to delete a key:value pair with `del`. If you store using a key that is already in use, the old value associated with that key is forgotten.

Extracting a value for a non-existent key by subscripting (`d[key]`) raises a `KeyError`. To avoid getting this error when trying to access a possibly non-existent key, use the `get` method instead, which returns `None` (or a specified default value) if the key is not in the dictionary.

Performing `list(d)` on a dictionary returns a list of all the keys used in the dictionary, in insertion order (if you want it sorted, just use `sorted(d)` instead). To check whether a single key is in the dictionary, use the `in` keyword.

Here is a small example using a dictionary:

    >>> tel = {'jack': 4098, 'sape': 4139}
    >>> tel['guido'] = 4127
    >>> tel
    {'jack': 4098, 'sape': 4139, 'guido': 4127}
    >>> tel['jack']
    4098
    >>> tel['irv']
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    KeyError: 'irv'
    >>> print(tel.get('irv'))
    None
    >>> del tel['sape']
    >>> tel['irv'] = 4127
    >>> tel
    {'jack': 4098, 'guido': 4127, 'irv': 4127}
    >>> list(tel)
    ['jack', 'guido', 'irv']
    >>> sorted(tel)
    ['guido', 'irv', 'jack']
    >>> 'guido' in tel
    True
    >>> 'jack' not in tel
    False

The `dict` constructor builds dictionaries directly from sequences of key-value pairs:

    >>> dict([('sape', 4139), ('guido', 4127), ('jack', 4098)])
    {'sape': 4139, 'guido': 4127, 'jack': 4098}
