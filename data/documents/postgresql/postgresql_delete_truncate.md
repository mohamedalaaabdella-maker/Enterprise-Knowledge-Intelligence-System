# PostgreSQL DELETE and TRUNCATE

Source: PostgreSQL Documentation
URL: https://www.postgresql.org/docs/18/sql-delete.html
Version: 18
License: PostgreSQL (license of the original documentation; this file is an excerpt reformatted as Markdown)

## DELETE

### Description

`DELETE` deletes rows that satisfy the `WHERE` clause from the specified table. If the `WHERE` clause is absent, the effect is to delete all rows in the table. The result is a valid, but empty table.

`TRUNCATE` provides a faster mechanism to remove all rows from a table.

There are two ways to delete rows in a table using information contained in other tables in the database: using sub-selects, or specifying additional tables in the `USING` clause. Which technique is more appropriate depends on the specific circumstances.

The optional `RETURNING` clause causes `DELETE` to compute and return value(s) based on each row actually deleted. Any expression using the table's columns, and/or columns of other tables mentioned in `USING`, can be computed. The syntax of the `RETURNING` list is identical to that of the output list of `SELECT`.

You must have the `DELETE` privilege on the table to delete from it, as well as the `SELECT` privilege for any table in the `USING` clause or whose values are read in the <condition>.

### Parameters

<with_query>
The `WITH` clause allows you to specify one or more subqueries that can be referenced by name in the `DELETE` query. See WITH Queries (Common Table Expressions) and SELECT for details.

<table_name>
The name (optionally schema-qualified) of the table to delete rows from. If `ONLY` is specified before the table name, matching rows are deleted from the named table only. If `ONLY` is not specified, matching rows are also deleted from any tables inheriting from the named table. Optionally, `*` can be specified after the table name to explicitly indicate that descendant tables are included.

<alias>
A substitute name for the target table. When an alias is provided, it completely hides the actual name of the table. For example, given `DELETE FROM foo AS f`, the remainder of the `DELETE` statement must refer to this table as `f` not `foo`.

<from_item>
A table expression allowing columns from other tables to appear in the `WHERE` condition. This uses the same syntax as the `FROM` clause of a `SELECT` statement; for example, an alias for the table name can be specified. Do not repeat the target table as a <from_item> unless you wish to set up a self-join (in which case it must appear with an alias in the <from_item>).

<condition>
An expression that returns a value of type `boolean`. Only rows for which this expression returns `true` will be deleted.

### Notes

PostgreSQL lets you reference columns of other tables in the `WHERE` condition by specifying the other tables in the `USING` clause. For example, to delete all films produced by a given producer, one can do:

    DELETE FROM films USING producers
      WHERE producer_id = producers.id AND producers.name = 'foo';

What is essentially happening here is a join between films and producers, with all successfully joined films rows being marked for deletion. This syntax is not standard. A more standard way to do it is:

    DELETE FROM films
      WHERE producer_id IN (SELECT id FROM producers WHERE name = 'foo');

In some cases the join style is easier to write or faster to execute than the sub-select style.

### Examples

Delete all films but musicals:

    DELETE FROM films WHERE kind <> 'Musical';

Clear the table `films`:

    DELETE FROM films;

Delete completed tasks, returning full details of the deleted rows:

    DELETE FROM tasks WHERE status = 'DONE' RETURNING *;

Delete the row of tasks on which the cursor `c_tasks` is currently positioned:

    DELETE FROM tasks WHERE CURRENT OF c_tasks;

While there is no `LIMIT` clause for `DELETE`, it is possible to get a similar effect using the same method described in the documentation of `UPDATE`:

    WITH delete_batch AS (
      SELECT l.ctid FROM user_logs AS l
        WHERE l.status = 'archived'
        ORDER BY l.creation_date
        FOR UPDATE
        LIMIT 10000
    )
    DELETE FROM user_logs AS dl
      USING delete_batch AS del
      WHERE dl.ctid = del.ctid;

This use of ctid is only safe because the query is repeatedly run, avoiding the problem of changed ctids.

## TRUNCATE

### Description

`TRUNCATE` quickly removes all rows from a set of tables. It has the same effect as an unqualified `DELETE` on each table, but since it does not actually scan the tables it is faster. Furthermore, it reclaims disk space immediately, rather than requiring a subsequent `VACUUM` operation. This is most useful on large tables.

### Parameters

<name>
The name (optionally schema-qualified) of a table to truncate. If `ONLY` is specified before the table name, only that table is truncated. If `ONLY` is not specified, the table and all its descendant tables (if any) are truncated. Optionally, `*` can be specified after the table name to explicitly indicate that descendant tables are included.

`RESTART IDENTITY`
Automatically restart sequences owned by columns of the truncated table(s).

`CONTINUE IDENTITY`
Do not change the values of sequences. This is the default.

`CASCADE`
Automatically truncate all tables that have foreign-key references to any of the named tables, or to any tables added to the group due to `CASCADE`.

`RESTRICT`
Refuse to truncate if any of the tables have foreign-key references from tables that are not listed in the command. This is the default.

### Notes

You must have the `TRUNCATE` privilege on a table to truncate it.

`TRUNCATE` acquires an `ACCESS EXCLUSIVE` lock on each table it operates on, which blocks all other concurrent operations on the table. When `RESTART IDENTITY` is specified, any sequences that are to be restarted are likewise locked exclusively. If concurrent access to a table is required, then the `DELETE` command should be used instead.

`TRUNCATE` cannot be used on a table that has foreign-key references from other tables, unless all such tables are also truncated in the same command. Checking validity in such cases would require table scans, and the whole point is not to do one. The `CASCADE` option can be used to automatically include all dependent tables — but be very careful when using this option, or else you might lose data you did not intend to! Note in particular that when the table to be truncated is a partition, siblings partitions are left untouched, but cascading occurs to all referencing tables and all their partitions with no distinction.

`TRUNCATE` will not fire any `ON DELETE` triggers that might exist for the tables. But it will fire `ON TRUNCATE` triggers. If `ON TRUNCATE` triggers are defined for any of the tables, then all `BEFORE TRUNCATE` triggers are fired before any truncation happens, and all `AFTER TRUNCATE` triggers are fired after the last truncation is performed and any sequences are reset. The triggers will fire in the order that the tables are to be processed (first those listed in the command, and then any that were added due to cascading).

`TRUNCATE` is not MVCC-safe. After truncation, the table will appear empty to concurrent transactions, if they are using a snapshot taken before the truncation occurred. See Caveats for more details.

`TRUNCATE` is transaction-safe with respect to the data in the tables: the truncation will be safely rolled back if the surrounding transaction does not commit.

When `RESTART IDENTITY` is specified, the implied `ALTER SEQUENCE RESTART` operations are also done transactionally; that is, they will be rolled back if the surrounding transaction does not commit. Be aware that if any additional sequence operations are done on the restarted sequences before the transaction rolls back, the effects of these operations on the sequences will be rolled back, but not their effects on `currval()`; that is, after the transaction `currval()` will continue to reflect the last sequence value obtained inside the failed transaction, even though the sequence itself may no longer be consistent with that. This is similar to the usual behavior of `currval()` after a failed transaction.

`TRUNCATE` can be used for foreign tables if supported by the foreign data wrapper, for instance, see postgres_fdw.

### Examples

Truncate the tables `bigtable` and `fattable`:

    TRUNCATE bigtable, fattable;

The same, and also reset any associated sequence generators:

    TRUNCATE bigtable, fattable RESTART IDENTITY;

Truncate the table `othertable`, and cascade to any tables that reference `othertable` via foreign-key constraints:

    TRUNCATE othertable CASCADE;
