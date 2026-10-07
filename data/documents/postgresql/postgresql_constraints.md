# PostgreSQL Constraints

Source: PostgreSQL Documentation
URL: https://www.postgresql.org/docs/18/ddl-constraints.html
Version: 18
License: PostgreSQL (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Constraints

Data types are a way to limit the kind of data that can be stored in a table. For many applications, however, the constraint they provide is too coarse. For example, a column containing a product price should probably only accept positive values. But there is no standard data type that accepts only positive numbers. Another issue is that you might want to constrain column data with respect to other columns or rows. For example, in a table containing product information, there should be only one row for each product number.

To that end, SQL allows you to define constraints on columns and tables. Constraints give you as much control over the data in your tables as you wish. If a user attempts to store data in a column that would violate a constraint, an error is raised. This applies even if the value came from the default value definition.

## Check Constraints

A check constraint is the most generic constraint type. It allows you to specify that the value in a certain column must satisfy a Boolean (truth-value) expression. For instance, to require positive product prices, you could use:

    CREATE TABLE products (
        product_no integer,
        name text,
        price numeric CHECK (price > 0)
    );

As you see, the constraint definition comes after the data type, just like default value definitions. Default values and constraints can be listed in any order. A check constraint consists of the key word `CHECK` followed by an expression in parentheses. The check constraint expression should involve the column thus constrained, otherwise the constraint would not make too much sense.

You can also give the constraint a separate name. This clarifies error messages and allows you to refer to the constraint when you need to change it. The syntax is:

    CREATE TABLE products (
        product_no integer,
        name text,
        price numeric CONSTRAINT positive_price CHECK (price > 0)
    );

So, to specify a named constraint, use the key word `CONSTRAINT` followed by an identifier followed by the constraint definition. (If you don't specify a constraint name in this way, the system chooses a name for you.)

A check constraint can also refer to several columns. Say you store a regular price and a discounted price, and you want to ensure that the discounted price is lower than the regular price:

    CREATE TABLE products (
        product_no integer,
        name text,
        price numeric CHECK (price > 0),
        discounted_price numeric CHECK (discounted_price > 0),
        CHECK (price > discounted_price)
    );

The first two constraints should look familiar. The third one uses a new syntax. It is not attached to a particular column, instead it appears as a separate item in the comma-separated column list. Column definitions and these constraint definitions can be listed in mixed order.

## Not-Null Constraints

A not-null constraint simply specifies that a column must not assume the null value. A syntax example:

    CREATE TABLE products (
        product_no integer NOT NULL,
        name text NOT NULL,
        price numeric
    );

An explicit constraint name can also be specified, for example:

    CREATE TABLE products (
        product_no integer NOT NULL,
        name text CONSTRAINT products_name_not_null NOT NULL,
        price numeric
    );

A not-null constraint is usually written as a column constraint. The syntax for writing it as a table constraint is

    CREATE TABLE products (
        product_no integer,
        name text,
        price numeric,
        NOT NULL product_no,
        NOT NULL name
    );

But this syntax is not standard and mainly intended for use by pg_dump.

A not-null constraint is functionally equivalent to creating a check constraint `CHECK (column_name IS NOT NULL)`, but in PostgreSQL creating an explicit not-null constraint is more efficient.

Of course, a column can have more than one constraint. Just write the constraints one after another:

    CREATE TABLE products (
        product_no integer NOT NULL,
        name text NOT NULL,
        price numeric NOT NULL CHECK (price > 0)
    );

## Unique Constraints

Unique constraints ensure that the data contained in a column, or a group of columns, is unique among all the rows in the table. The syntax is:

    CREATE TABLE products (
        product_no integer UNIQUE,
        name text,
        price numeric
    );

when written as a column constraint, and:

    CREATE TABLE products (
        product_no integer,
        name text,
        price numeric,
        UNIQUE (product_no)
    );

when written as a table constraint.

To define a unique constraint for a group of columns, write it as a table constraint with the column names separated by commas:

    CREATE TABLE example (
        a integer,
        b integer,
        c integer,
        UNIQUE (a, c)
    );

This specifies that the combination of values in the indicated columns is unique across the whole table, though any one of the columns need not be (and ordinarily isn't) unique.

You can assign your own name for a unique constraint, in the usual way:

    CREATE TABLE products (
        product_no integer CONSTRAINT must_be_different UNIQUE,
        name text,
        price numeric
    );

Adding a unique constraint will automatically create a unique B-tree index on the column or group of columns listed in the constraint. A uniqueness restriction covering only some rows cannot be written as a unique constraint, but it is possible to enforce such a restriction by creating a unique partial index.

## Primary Keys

A primary key constraint indicates that a column, or group of columns, can be used as a unique identifier for rows in the table. This requires that the values be both unique and not null. So, the following two table definitions accept the same data:

    CREATE TABLE products (
        product_no integer UNIQUE NOT NULL,
        name text,
        price numeric
    );

    CREATE TABLE products (
        product_no integer PRIMARY KEY,
        name text,
        price numeric
    );

Primary keys can span more than one column; the syntax is similar to unique constraints:

    CREATE TABLE example (
        a integer,
        b integer,
        c integer,
        PRIMARY KEY (a, c)
    );

Adding a primary key will automatically create a unique B-tree index on the column or group of columns listed in the primary key, and will force the column(s) to be marked `NOT NULL`.

A table can have at most one primary key. (There can be any number of unique constraints, which combined with not-null constraints are functionally almost the same thing, but only one can be identified as the primary key.) Relational database theory dictates that every table must have a primary key. This rule is not enforced by PostgreSQL, but it is usually best to follow it.

## Foreign Keys

A foreign key constraint specifies that the values in a column (or a group of columns) must match the values appearing in some row of another table. We say this maintains the referential integrity between two related tables.

Say you have the product table that we have used several times already:

    CREATE TABLE products (
        product_no integer PRIMARY KEY,
        name text,
        price numeric
    );

Let's also assume you have a table storing orders of those products. We want to ensure that the orders table only contains orders of products that actually exist. So we define a foreign key constraint in the orders table that references the products table:

    CREATE TABLE orders (
        order_id integer PRIMARY KEY,
        product_no integer REFERENCES products (product_no),
        quantity integer
    );

Now it is impossible to create orders with non-NULL product_no entries that do not appear in the products table.

We say that in this situation the orders table is the referencing table and the products table is the referenced table. Similarly, there are referencing and referenced columns.

You can also shorten the above command to:

    CREATE TABLE orders (
        order_id integer PRIMARY KEY,
        product_no integer REFERENCES products,
        quantity integer
    );

because in absence of a column list the primary key of the referenced table is used as the referenced column(s).

You can assign your own name for a foreign key constraint, in the usual way.

A foreign key can also constrain and reference a group of columns. As usual, it then needs to be written in table constraint form. Here is a contrived syntax example:

    CREATE TABLE t1 (
      a integer PRIMARY KEY,
      b integer,
      c integer,
      FOREIGN KEY (b, c) REFERENCES other_table (c1, c2)
    );

Of course, the number and type of the constrained columns need to match the number and type of the referenced columns.

Sometimes it is useful for the “other table” of a foreign key constraint to be the same table; this is called a self-referential foreign key. For example, if you want rows of a table to represent nodes of a tree structure, you could write

    CREATE TABLE tree (
        node_id integer PRIMARY KEY,
        parent_id integer REFERENCES tree,
        name text,
        ...
    );

A top-level node would have NULL parent_id, while non-NULL parent_id entries would be constrained to reference valid rows of the table.
