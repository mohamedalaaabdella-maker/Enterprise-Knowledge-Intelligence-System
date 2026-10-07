# PostgreSQL JOINs

Source: PostgreSQL Documentation
URL: https://www.postgresql.org/docs/18/queries-table-expressions.html#QUERIES-JOIN
Version: 18
License: PostgreSQL (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Joined Tables (JOIN Types and Conditions)

A joined table is a table derived from two other (real or derived) tables according to the rules of the particular join type. Inner, outer, and cross-joins are available. The general syntax of a joined table is <T1> <join_type> <T2> [<join_condition>] Joins of all types can be chained together, or nested: either or both <T1> and <T2> can be joined tables. Parentheses can be used around `JOIN` clauses to control the join order. In the absence of parentheses, `JOIN` clauses nest left-to-right.

Cross join
T1

CROSS JOIN

T2

For every possible combination of rows from <T1> and <T2> (i.e., a Cartesian product), the joined table will contain a row consisting of all columns in <T1> followed by all columns in <T2>. If the tables have N and M rows respectively, the joined table will have N \* M rows.

`FROM T1 CROSS JOIN T2` is equivalent to `FROM T1 INNER JOIN T2 ON TRUE` (see below). It is also equivalent to `FROM T1, T2`.

This latter equivalence does not hold exactly when more than two tables appear, because `JOIN` binds more tightly than comma. For example `FROM T1 CROSS JOIN T2 INNER JOIN T3 ON condition` is not the same as `FROM T1, T2 INNER JOIN T3 ON condition` because the <condition> can reference <T1> in the first case but not the second.

Qualified joins
T1

{

INNER

\| { LEFT \| RIGHT \| FULL }

OUTER

} JOIN

T2

ON

boolean_expression

T1

{

INNER

\| { LEFT \| RIGHT \| FULL }

OUTER

} JOIN

T2

USING (

join column list

)

T1

NATURAL {

INNER

\| { LEFT \| RIGHT \| FULL }

OUTER

} JOIN

T2

The words `INNER` and `OUTER` are optional in all forms. `INNER` is the default; `LEFT`, `RIGHT`, and `FULL` imply an outer join.

The join condition is specified in the `ON` or `USING` clause, or implicitly by the word `NATURAL`. The join condition determines which rows from the two source tables are considered to “match”, as explained in detail below.

The possible types of qualified join are:

`INNER JOIN`
For each row R1 of T1, the joined table has a row for each row in T2 that satisfies the join condition with R1.

`LEFT OUTER JOIN`
First, an inner join is performed. Then, for each row in T1 that does not satisfy the join condition with any row in T2, a joined row is added with null values in columns of T2. Thus, the joined table always has at least one row for each row in T1.

`RIGHT OUTER JOIN`
First, an inner join is performed. Then, for each row in T2 that does not satisfy the join condition with any row in T1, a joined row is added with null values in columns of T1. This is the converse of a left join: the result table will always have a row for each row in T2.

`FULL OUTER JOIN`
First, an inner join is performed. Then, for each row in T1 that does not satisfy the join condition with any row in T2, a joined row is added with null values in columns of T2. Also, for each row of T2 that does not satisfy the join condition with any row in T1, a joined row with null values in the columns of T1 is added.

The `ON` clause is the most general kind of join condition: it takes a Boolean value expression of the same kind as is used in a `WHERE` clause. A pair of rows from <T1> and <T2> match if the `ON` expression evaluates to true.

The `USING` clause is a shorthand that allows you to take advantage of the specific situation where both sides of the join use the same name for the joining column(s). It takes a comma-separated list of the shared column names and forms a join condition that includes an equality comparison for each one. For example, joining <T1> and <T2> with `USING (a, b)` produces the join condition `ON T1.a = T2.a AND T1.b = T2.b`.

Furthermore, the output of `JOIN USING` suppresses redundant columns: there is no need to print both of the matched columns, since they must have equal values. While `JOIN ON` produces all columns from <T1> followed by all columns from <T2>, `JOIN USING` produces one output column for each of the listed column pairs (in the listed order), followed by any remaining columns from <T1>, followed by any remaining columns from <T2>.

Finally, `NATURAL` is a shorthand form of `USING`: it forms a `USING` list consisting of all column names that appear in both input tables. As with `USING`, these columns appear only once in the output table. If there are no common column names, `NATURAL JOIN` behaves like `CROSS JOIN`.

`USING` is reasonably safe from column changes in the joined relations since only the listed columns are combined. `NATURAL` is considerably more risky since any schema changes to either relation that cause a new matching column name to be present will cause the join to combine that new column as well.

To put this together, assume we have tables `t1`:

     num | name
    -----+------
       1 | a
       2 | b
       3 | c

and `t2`:

     num | value
    -----+-------
       1 | xxx
       3 | yyy
       5 | zzz

then we get the following results for the various joins:

    => SELECT * FROM t1 CROSS JOIN t2;
     num | name | num | value
    -----+------+-----+-------
       1 | a    |   1 | xxx
       1 | a    |   3 | yyy
       1 | a    |   5 | zzz
       2 | b    |   1 | xxx
       2 | b    |   3 | yyy
       2 | b    |   5 | zzz
       3 | c    |   1 | xxx
       3 | c    |   3 | yyy
       3 | c    |   5 | zzz
    (9 rows)

    => SELECT * FROM t1 INNER JOIN t2 ON t1.num = t2.num;
     num | name | num | value
    -----+------+-----+-------
       1 | a    |   1 | xxx
       3 | c    |   3 | yyy
    (2 rows)

## Joins Between Tables (Tutorial)

Thus far, our queries have only accessed one table at a time. Queries can access multiple tables at once, or access the same table in such a way that multiple rows of the table are being processed at the same time. Queries that access multiple tables (or multiple instances of the same table) at one time are called join queries. They combine rows from one table with rows from a second table, with an expression specifying which rows are to be paired. For example, to return all the weather records together with the location of the associated city, the database needs to compare the city column of each row of the weather table with the name column of all rows in the cities table, and select the pairs of rows where these values match. This would be accomplished by the following query:

    SELECT * FROM weather JOIN cities ON city = name;

         city      | temp_lo | temp_hi | prcp |    date    |     name      | location
    ---------------+---------+---------+------+------------+---------------+-----------
     San Francisco |      46 |      50 | 0.25 | 1994-11-27 | San Francisco | (-194,53)
     San Francisco |      43 |      57 |    0 | 1994-11-29 | San Francisco | (-194,53)
    (2 rows)

Observe two things about the result set:

- There is no result row for the city of Hayward. This is because there is no matching entry in the cities table for Hayward, so the join ignores the unmatched rows in the weather table. We will see shortly how this can be fixed.

- There are two columns containing the city name. This is correct because the lists of columns from the weather and cities tables are concatenated. In practice this is undesirable, though, so you will probably want to list the output columns explicitly rather than using `*`:

      SELECT city, temp_lo, temp_hi, prcp, date, location
          FROM weather JOIN cities ON city = name;

Since the columns all had different names, the parser automatically found which table they belong to. If there were duplicate column names in the two tables you'd need to qualify the column names to show which one you meant, as in:

    SELECT weather.city, weather.temp_lo, weather.temp_hi,
           weather.prcp, weather.date, cities.location
        FROM weather JOIN cities ON weather.city = cities.name;

It is widely considered good style to qualify all column names in a join query, so that the query won't fail if a duplicate column name is later added to one of the tables.

Join queries of the kind seen thus far can also be written in this form:

    SELECT *
        FROM weather, cities
        WHERE city = name;

This syntax pre-dates the `JOIN`/`ON` syntax, which was introduced in SQL-92. The tables are simply listed in the `FROM` clause, and the comparison expression is added to the `WHERE` clause. The results from this older implicit syntax and the newer explicit `JOIN`/`ON` syntax are identical. But for a reader of the query, the explicit syntax makes its meaning easier to understand: The join condition is introduced by its own key word whereas previously the condition was mixed into the `WHERE` clause together with other conditions.
