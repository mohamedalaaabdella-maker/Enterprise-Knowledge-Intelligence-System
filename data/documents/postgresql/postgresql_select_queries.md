# PostgreSQL SELECT Queries

Source: PostgreSQL Documentation
URL: https://www.postgresql.org/docs/18/queries.html
Version: 18
License: PostgreSQL (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Overview

The process of retrieving or the command to retrieve data from a database is called a query. In SQL the `SELECT` command is used to specify queries. The general syntax of the `SELECT` command is [WITH <with_queries>] SELECT <select_list> FROM <table_expression> [<sort_specification>] The following sections describe the details of the select list, the table expression, and the sort specification. `WITH` queries are treated last since they are an advanced feature.

A simple kind of query has the form:

    SELECT * FROM table1;

Assuming that there is a table called `table1`, this command would retrieve all rows and all user-defined columns from `table1`. (The method of retrieval depends on the client application. For example, the psql program will display an ASCII-art table on the screen, while client libraries will offer functions to extract individual values from the query result.) The select list specification `*` means all columns that the table expression happens to provide. A select list can also select a subset of the available columns or make calculations using the columns. For example, if `table1` has columns named `a`, `b`, and `c` (and perhaps others) you can make the following query:

    SELECT a, b + c FROM table1;

(assuming that `b` and `c` are of a numerical data type). See Select Lists for more details.

`FROM table1` is a simple kind of table expression: it reads just one table. In general, table expressions can be complex constructs of base tables, joins, and subqueries. But you can also omit the table expression entirely and use the `SELECT` command as a calculator:

    SELECT 3 * 4;

This is more useful if the expressions in the select list return varying results. For example, you could call a function this way:

    SELECT random();

## The WHERE Clause

The syntax of the `WHERE` clause is WHERE <search_condition> where <search_condition> is any value expression (see Value Expressions) that returns a value of type `boolean`.

After the processing of the `FROM` clause is done, each row of the derived virtual table is checked against the search condition. If the result of the condition is true, the row is kept in the output table, otherwise (i.e., if the result is false or null) it is discarded. The search condition typically references at least one column of the table generated in the `FROM` clause; this is not required, but otherwise the `WHERE` clause will be fairly useless.

The join condition of an inner join can be written either in the `WHERE` clause or in the `JOIN` clause. For example, these table expressions are equivalent:

    FROM a, b WHERE a.id = b.id AND b.val > 5

and:

    FROM a INNER JOIN b ON (a.id = b.id) WHERE b.val > 5

or perhaps even:

    FROM a NATURAL JOIN b WHERE b.val > 5

Which one of these you use is mainly a matter of style. The `JOIN` syntax in the `FROM` clause is probably not as portable to other SQL database management systems, even though it is in the SQL standard. For outer joins there is no choice: they must be done in the `FROM` clause. The `ON` or `USING` clause of an outer join is *not* equivalent to a `WHERE` condition, because it results in the addition of rows (for unmatched input rows) as well as the removal of rows in the final result.

Here are some examples of `WHERE` clauses:

    SELECT ... FROM fdt WHERE c1 > 5

    SELECT ... FROM fdt WHERE c1 IN (1, 2, 3)

    SELECT ... FROM fdt WHERE c1 IN (SELECT c1 FROM t2)

    SELECT ... FROM fdt WHERE c1 IN (SELECT c3 FROM t2 WHERE c2 = fdt.c1 + 10)

    SELECT ... FROM fdt WHERE c1 BETWEEN (SELECT c3 FROM t2 WHERE c2 = fdt.c1 + 10) AND 100

## The GROUP BY and HAVING Clauses

After passing the `WHERE` filter, the derived input table might be subject to grouping, using the `GROUP BY` clause, and elimination of group rows using the `HAVING` clause.

SELECT

select_list

FROM ...

WHERE ...

GROUP BY

grouping_column_reference

,

grouping_column_reference

...

The `GROUP BY` clause is used to group together those rows in a table that have the same values in all the columns listed. The order in which the columns are listed does not matter. The effect is to combine each set of rows having common values into one group row that represents all rows in the group. This is done to eliminate redundancy in the output and/or compute aggregates that apply to these groups. For instance:

    => SELECT * FROM test1;
     x | y
    ---+---
     a | 3
     c | 2
     b | 5
     a | 1
    (4 rows)

    => SELECT x FROM test1 GROUP BY x;
     x
    ---
     a
     b
     c
    (3 rows)

In the second query, we could not have written `SELECT * FROM test1 GROUP BY x`, because there is no single value for the column `y` that could be associated with each group. The grouped-by columns can be referenced in the select list since they have a single value in each group.

In general, if a table is grouped, columns that are not listed in `GROUP BY` cannot be referenced except in aggregate expressions. An example with aggregate expressions is:

    => SELECT x, sum(y) FROM test1 GROUP BY x;
     x | sum
    ---+-----
     a |   4
     b |   5
     c |   2
    (3 rows)

Here `sum` is an aggregate function that computes a single value over the entire group. More information about the available aggregate functions can be found in Aggregate Functions.

Grouping without aggregate expressions effectively calculates the set of distinct values in a column. This can also be achieved using the `DISTINCT` clause (see DISTINCT).

## Sorting Rows (ORDER BY)

After a query has produced an output table (after the select list has been processed) it can optionally be sorted. If sorting is not chosen, the rows will be returned in an unspecified order. The actual order in that case will depend on the scan and join plan types and the order on disk, but it must not be relied on. A particular output ordering can only be guaranteed if the sort step is explicitly chosen.

The `ORDER BY` clause specifies the sort order: SELECT <select_list> FROM <table_expression> ORDER BY <sort_expression1> [ASC \| DESC] [NULLS { FIRST \| LAST }] [, <sort_expression2> [ASC \| DESC] [NULLS { FIRST \| LAST }] ...] The sort expression(s) can be any expression that would be valid in the query's select list. An example is:

    SELECT a, b FROM table1 ORDER BY a + b, c;

When more than one expression is specified, the later values are used to sort rows that are equal according to the earlier values. Each expression can be followed by an optional `ASC` or `DESC` keyword to set the sort direction to ascending or descending. `ASC` order is the default. Ascending order puts smaller values first, where “smaller” is defined in terms of the `<` operator. Similarly, descending order is determined with the `>` operator.

The `NULLS FIRST` and `NULLS LAST` options can be used to determine whether nulls appear before or after non-null values in the sort ordering. By default, null values sort as if larger than any non-null value; that is, `NULLS FIRST` is the default for `DESC` order, and `NULLS LAST` otherwise.

Note that the ordering options are considered independently for each sort column. For example `ORDER BY x, y DESC` means `ORDER BY x ASC, y DESC`, which is not the same as `ORDER BY x DESC, y DESC`.

## LIMIT and OFFSET

`LIMIT` and `OFFSET` allow you to retrieve just a portion of the rows that are generated by the rest of the query: SELECT <select_list> FROM <table_expression> [ORDER BY ...] [LIMIT { <count> \| ALL }] [OFFSET <start>]

If a limit count is given, no more than that many rows will be returned (but possibly fewer, if the query itself yields fewer rows). `LIMIT ALL` is the same as omitting the `LIMIT` clause, as is `LIMIT` with a NULL argument.

`OFFSET` says to skip that many rows before beginning to return rows. `OFFSET 0` is the same as omitting the `OFFSET` clause, as is `OFFSET` with a NULL argument.

If both `OFFSET` and `LIMIT` appear, then `OFFSET` rows are skipped before starting to count the `LIMIT` rows that are returned.

When using `LIMIT`, it is important to use an `ORDER BY` clause that constrains the result rows into a unique order. Otherwise you will get an unpredictable subset of the query's rows. You might be asking for the tenth through twentieth rows, but tenth through twentieth in what ordering? The ordering is unknown, unless you specified `ORDER BY`.

## WITH Queries (Common Table Expressions)

`WITH` provides a way to write auxiliary statements for use in a larger query. These statements, which are often referred to as Common Table Expressions or CTEs, can be thought of as defining temporary tables that exist just for one query. Each auxiliary statement in a `WITH` clause can be a `SELECT`, `INSERT`, `UPDATE`, `DELETE`, or `MERGE`; and the `WITH` clause itself is attached to a primary statement that can also be a `SELECT`, `INSERT`, `UPDATE`, `DELETE`, or `MERGE`.

The basic value of `SELECT` in `WITH` is to break down complicated queries into simpler parts. An example is:

    WITH regional_sales AS (
        SELECT region, SUM(amount) AS total_sales
        FROM orders
        GROUP BY region
    ), top_regions AS (
        SELECT region
        FROM regional_sales
        WHERE total_sales > (SELECT SUM(total_sales)/10 FROM regional_sales)
    )
    SELECT region,
           product,
           SUM(quantity) AS product_units,
           SUM(amount) AS product_sales
    FROM orders
    WHERE region IN (SELECT region FROM top_regions)
    GROUP BY region, product;

which displays per-product sales totals in only the top sales regions. The `WITH` clause defines two auxiliary statements named regional_sales and top_regions, where the output of regional_sales is used in top_regions and the output of top_regions is used in the primary `SELECT` query. This example could have been written without `WITH`, but we'd have needed two levels of nested sub-`SELECT`s. It's a bit easier to follow this way.
