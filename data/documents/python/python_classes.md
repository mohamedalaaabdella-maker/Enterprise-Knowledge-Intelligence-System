# Python Classes and Objects

Source: Python Documentation
URL: https://docs.python.org/3.14/tutorial/classes.html
Version: 3.14
License: PSF-2.0 (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Class Definition Syntax

The simplest form of class definition looks like this:

    class ClassName:
        <statement-1>
        .
        .
        .
        <statement-N>

Class definitions, like function definitions (`def` statements) must be executed before they have any effect. (You could conceivably place a class definition in a branch of an `if` statement, or inside a function.)

In practice, the statements inside a class definition will usually be function definitions, but other statements are allowed, and sometimes useful --- we'll come back to this later. The function definitions inside a class normally have a peculiar form of argument list, dictated by the calling conventions for methods --- again, this is explained later.

When a class definition is entered, a new namespace is created, and used as the local scope --- thus, all assignments to local variables go into this new namespace. In particular, function definitions bind the name of the new function here.

When a class definition is left normally (via the end), a *class object* is created. This is basically a wrapper around the contents of the namespace created by the class definition; we'll learn more about class objects in the next section. The original local scope (the one in effect just before the class definition was entered) is reinstated, and the class object is bound here to the class name given in the class definition header (`ClassName` in the example).

## Class Objects

Class objects support two kinds of operations: attribute references and instantiation.

*Attribute references* use the standard syntax used for all attribute references in Python: `obj.name`. Valid attribute names are all the names that were in the class's namespace when the class object was created. So, if the class definition looked like this:

    class MyClass:
        """A simple example class"""
        i = 12345

        def f(self):
            return 'hello world'

then `MyClass.i` and `MyClass.f` are valid attribute references, returning an integer and a function object, respectively. Class attributes can also be assigned to, so you can change the value of `MyClass.i` by assignment. `__doc__` is also a valid attribute, returning the docstring belonging to the class: `"A simple example class"`.

Class *instantiation* uses function notation. Just pretend that the class object is a parameterless function that returns a new instance of the class. For example (assuming the above class):

    x = MyClass()

creates a new *instance* of the class and assigns this object to the local variable `x`.

The instantiation operation ("calling" a class object) creates an empty object. Many classes like to create objects with instances customized to a specific initial state. Therefore a class may define a special method named `__init__`, like this:

    def __init__(self):
        self.data = []

When a class defines an `__init__` method, class instantiation automatically invokes `__init__` for the newly created class instance. So in this example, a new, initialized instance can be obtained by:

    x = MyClass()

## Instance Objects

Now what can we do with instance objects? The only operations understood by instance objects are attribute references. There are two kinds of valid attribute names: data attributes and methods.

*Data attributes* correspond to "instance variables" in Smalltalk, and to "data members" in C++. Data attributes need not be declared; like local variables, they spring into existence when they are first assigned to. For example, if `x` is the instance of `MyClass` created above, the following piece of code will print the value `16`, without leaving a trace:

    x.counter = 1
    while x.counter < 10:
        x.counter = x.counter * 2
    print(x.counter)
    del x.counter

The other kind of instance attribute reference is a *method*. A method is a function that "belongs to" an object.

Valid method names of an instance object depend on its class. By definition, all attributes of a class that are function objects define corresponding methods of its instances. So in our example, `x.f` is a valid method reference, since `MyClass.f` is a function, but `x.i` is not, since `MyClass.i` is not. But `x.f` is not the same thing as `MyClass.f` --- it is a *method object*, not a function object.

## Method Objects

Usually, a method is called right after it is bound:

    x.f()

If `x = MyClass()`, as above, this will return the string `'hello world'`. However, it is not necessary to call a method right away: `x.f` is a method object, and can be stored away and called at a later time. For example:

    xf = x.f
    while True:
        print(xf())

will continue to print `hello world` until the end of time.

What exactly happens when a method is called? You may have noticed that `x.f()` was called without an argument above, even though the function definition for `f` specified an argument. What happened to the argument? Surely Python raises an exception when a function that requires an argument is called without any --- even if the argument isn't actually used...

Actually, you may have guessed the answer: the special thing about methods is that the instance object is passed as the first argument of the function. In our example, the call `x.f()` is exactly equivalent to `MyClass.f(x)`. In general, calling a method with a list of *n* arguments is equivalent to calling the corresponding function with an argument list that is created by inserting the method's instance object before the first argument.

## Class and Instance Variables

Generally speaking, instance variables are for data unique to each instance and class variables are for attributes and methods shared by all instances of the class:

    class Dog:

        kind = 'canine'         # class variable shared by all instances

        def __init__(self, name):
            self.name = name    # instance variable unique to each instance

    >>> d = Dog('Fido')
    >>> e = Dog('Buddy')
    >>> d.kind                  # shared by all dogs
    'canine'
    >>> e.kind                  # shared by all dogs
    'canine'
    >>> d.name                  # unique to d
    'Fido'
    >>> e.name                  # unique to e
    'Buddy'

As discussed in A Word About Names and Objects, shared data can have possibly surprising effects involving `mutable` objects such as lists and dictionaries. For example, the *tricks* list in the following code should not be used as a class variable because just a single list would be shared by all *Dog* instances:

    class Dog:

        tricks = []             # mistaken use of a class variable

        def __init__(self, name):
            self.name = name

        def add_trick(self, trick):
            self.tricks.append(trick)

    >>> d = Dog('Fido')
    >>> e = Dog('Buddy')
    >>> d.add_trick('roll over')
    >>> e.add_trick('play dead')
    >>> d.tricks                # unexpectedly shared by all dogs
    ['roll over', 'play dead']

Correct design of the class should use an instance variable instead:

    class Dog:

        def __init__(self, name):
            self.name = name
            self.tricks = []    # creates a new empty list for each dog

        def add_trick(self, trick):
            self.tricks.append(trick)

    >>> d = Dog('Fido')
    >>> e = Dog('Buddy')
    >>> d.add_trick('roll over')
    >>> e.add_trick('play dead')
    >>> d.tricks
    ['roll over']
    >>> e.tricks
    ['play dead']

## Inheritance

Of course, a language feature would not be worthy of the name "class" without supporting inheritance. The syntax for a derived class definition looks like this:

    class DerivedClassName(BaseClassName):
        <statement-1>
        .
        .
        .
        <statement-N>

The name `BaseClassName` must be defined in a namespace accessible from the scope containing the derived class definition. In place of a base class name, other arbitrary expressions are also allowed. This can be useful, for example, when the base class is defined in another module:

    class DerivedClassName(modname.BaseClassName):

Execution of a derived class definition proceeds the same as for a base class. When the class object is constructed, the base class is remembered. This is used for resolving attribute references: if a requested attribute is not found in the class, the search proceeds to look in the base class. This rule is applied recursively if the base class itself is derived from some other class.

There's nothing special about instantiation of derived classes: `DerivedClassName()` creates a new instance of the class. Method references are resolved as follows: the corresponding class attribute is searched, descending down the chain of base classes if necessary, and the method reference is valid if this yields a function object.

Derived classes may override methods of their base classes. Because methods have no special privileges when calling other methods of the same object, a method of a base class that calls another method defined in the same base class may end up calling a method of a derived class that overrides it. (For C++ programmers: all methods in Python are effectively `virtual`.)

An overriding method in a derived class may in fact want to extend rather than simply replace the base class method of the same name. There is a simple way to call the base class method directly: just call `BaseClassName.methodname(self, arguments)`. This is occasionally useful to clients as well. (Note that this only works if the base class is accessible as `BaseClassName` in the global scope.)
