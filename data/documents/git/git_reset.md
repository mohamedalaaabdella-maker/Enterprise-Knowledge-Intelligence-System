# Git Reset

Source: Git Documentation
URL: https://git-scm.com/docs/git-reset
Version: 2.55.0
License: GPL-2.0-only (license of the original documentation; this file is an excerpt reformatted as Markdown)

## DESCRIPTION

`git reset` does either of the following:

1. `git reset [<mode>] <commit>` changes which commit `HEAD` points to. This
   makes it possible to undo various Git operations, for example commit, merge,
   rebase, and pull.
2. When you specify files or directories or pass `--patch`, `git reset` updates
   the staged version of the specified files.

**`git reset [<mode>] [<commit>]`**

Set the current branch head (`HEAD`) to point at _<commit>_.
Depending on _<mode>_, also update the working directory and/or index
to match the contents of _<commit>_.
_<commit>_ defaults to `HEAD`.
Before the operation, `ORIG_HEAD` is set to the tip of the current branch.

The _<mode>_ must be one of the following (default `--mixed`):

**`--mixed`**

Leave your working directory unchanged.
Update the index to match the new `HEAD`, so nothing will be staged.

If `-N` is specified, mark removed paths as intent-to-add (see
git-add(1)).

**`--soft`**

Leave your working tree files and the index unchanged.
For example, if you have no staged changes, you can use
`git reset --soft HEAD~5; git commit`
to combine the last 5 commits into 1 commit. This works even with
changes in the working tree, which are left untouched, but such usage
can lead to confusion.

**`--hard`**

Overwrite all files and directories with the version from _<commit>_,
and may overwrite untracked files. Tracked files not in _<commit>_ are
removed so that the working tree matches _<commit>_.
Update the index to match the new `HEAD`, so nothing will be staged.

**`--merge`**

Reset the index and update the files in the working tree that are
different between _<commit>_ and `HEAD`, but keep those which are
different between the index and working tree (i.e. which have changes
which have not been added).
Mainly exists to reset unmerged index entries, like those left behind by
`git am -3` or `git switch -m` in certain situations.
If a file that is different between _<commit>_ and the index has
unstaged changes, reset is aborted.

**`--keep`**

Resets index entries and updates files in the working tree that are
different between _<commit>_ and `HEAD`.
If a file that is different between _<commit>_ and `HEAD` has local
changes, reset is aborted.

**`--recurse-submodules`**

**`--no-recurse-submodules`**

When the working tree is updated, using `--recurse-submodules` will
also recursively reset the working tree of all active submodules
according to the commit recorded in the superproject, also setting
the submodules' `HEAD` to be detached at that commit.

**`git reset [-q] [<tree-ish>] [--] <pathspec>...`**

**`git reset [-q] [--pathspec-from-file=<file> [--pathspec-file-nul]] [<tree-ish>]`**

For all specified files or directories, set the staged version to
the version from the given commit or tree (which defaults to `HEAD`).

This means that `git reset <pathspec>` is the opposite of `git add
<pathspec>`: it unstages all changes to the specified file(s) or
directories. This is equivalent to `git restore --staged <pathspec>...`.

In this mode, `git reset` updates only the index (without updating the `HEAD` or
working tree files). If you want to update the files as well as the index
entries, use git-restore(1).

**`git reset (--patch | -p) [<tree-ish>] [--] [<pathspec>...]`**

Interactively select changes from the difference between the index
and the specified commit or tree (which defaults to `HEAD`).
The index is modified using the chosen changes.

This means that `git reset -p` is the opposite of `git add -p`, i.e.
you can use it to selectively unstage changes. See the "Interactive Mode"
section of git-add(1) to learn how to use the `--patch` option.

See "Reset, restore and revert" in git(1) for the differences
between the three commands.

## EXAMPLES

**Undo add**

```
$ edit                                     <1>
$ git add frotz.c filfre.c
$ mailx                                    <2>
$ git reset                                <3>
$ git pull git://info.example.com/ nitfol  <4>
```

<1> You are happily working on something, and find the changes
    in these files are in good order.  You do not want to see them
    when you run `git diff`, because you plan to work on other files
    and changes with these files are distracting.
<2> Somebody asks you to pull, and the changes sound worthy of merging.
<3> However, you already dirtied the index (i.e. your index does
    not match the `HEAD` commit).  But you know the pull you are going
    to make does not affect `frotz.c` or `filfre.c`, so you revert the
    index changes for these two files.  Your changes in working tree
    remain there.
<4> Then you can pull and merge, leaving `frotz.c` and `filfre.c`
    changes still in the working tree.

**Undo a commit and redo**

```
$ git commit ...
$ git reset --soft HEAD^      <1>
$ edit                        <2>
$ git commit -a -c ORIG_HEAD  <3>
```

<1> This is most often done when you remembered what you
    just committed is incomplete, or you misspelled your commit
    message, or both.  Leaves working tree as it was before "reset".
<2> Make corrections to working tree files.
<3> "reset" copies the old head to `.git/ORIG_HEAD`; redo the
    commit by starting with its log message.  If you do not need to
    edit the message further, you can give `-C` option instead.

See also the `--amend` option to git-commit(1).

**Undo a commit, making it a topic branch**

```
$ git branch topic/wip          <1>
$ git reset --hard HEAD~3       <2>
$ git switch topic/wip          <3>
```

<1> You have made some commits, but realize they were premature
    to be in the `master` branch.  You want to continue polishing
    them in a topic branch, so create `topic/wip` branch off of the
    current `HEAD`.
<2> Rewind the master branch to get rid of those three commits.
<3> Switch to `topic/wip` branch and keep working.

**Undo commits permanently**

```
$ git commit ...
$ git reset --hard HEAD~3   <1>
```

<1> The last three commits (`HEAD`, `HEAD^`, and `HEAD~2`) were bad
    and you do not want to ever see them again.  Do *not* do this if
    you have already given these commits to somebody else.  (See the
    "RECOVERING FROM UPSTREAM REBASE" section in git-rebase(1)
    for the implications of doing so.)

**Undo a merge or pull**

```
$ git pull                         <1>
Auto-merging nitfol
CONFLICT (content): Merge conflict in nitfol
Automatic merge failed; fix conflicts and then commit the result.
$ git reset --hard                 <2>
$ git pull . topic/branch          <3>
Updating from 41223... to 13134...
Fast-forward
$ git reset --hard ORIG_HEAD       <4>
```

<1> Try to update from the upstream resulted in a lot of
    conflicts; you were not ready to spend a lot of time merging
    right now, so you decide to do that later.
<2> "pull" has not made merge commit, so `git reset --hard`
    which is a synonym for `git reset --hard HEAD` clears the mess
    from the index file and the working tree.
<3> Merge a topic branch into the current branch, which resulted
    in a fast-forward.
<4> But you decided that the topic branch is not ready for public
    consumption yet.  "pull" or "merge" always leaves the original
    tip of the current branch in `ORIG_HEAD`, so resetting hard to it
    brings your index file and the working tree back to that state,
    and resets the tip of the branch to that commit.

## DISCUSSION

The tables below show what happens when running:

```
git reset --option target
```

to reset the `HEAD` to another commit (`target`) with the different
reset options depending on the state of the files.

In these tables, `A`, `B`, `C` and `D` are some different states of a
file. For example, the first line of the first table means that if a
file is in state `A` in the working tree, in state `B` in the index, in
state `C` in `HEAD` and in state `D` in the target, then `git reset --soft
target` will leave the file in the working tree in state `A` and in the
index in state `B`.  It resets (i.e. moves) the `HEAD` (i.e. the tip of
the current branch, if you are on one) to `target` (which has the file
in state `D`).

```
working index HEAD target         working index HEAD
----------------------------------------------------
 A       B     C    D     --soft   A       B     D
			  --mixed  A       D     D
			  --hard   D       D     D
			  --merge (disallowed)
			  --keep  (disallowed)
```

```
working index HEAD target         working index HEAD
----------------------------------------------------
 A       B     C    C     --soft   A       B     C
			  --mixed  A       C     C
			  --hard   C       C     C
			  --merge (disallowed)
			  --keep   A       C     C
```

```
working index HEAD target         working index HEAD
----------------------------------------------------
 B       B     C    D     --soft   B       B     D
			  --mixed  B       D     D
			  --hard   D       D     D
			  --merge  D       D     D
			  --keep  (disallowed)
```

```
working index HEAD target         working index HEAD
----------------------------------------------------
 B       B     C    C     --soft   B       B     C
			  --mixed  B       C     C
			  --hard   C       C     C
			  --merge  C       C     C
			  --keep   B       C     C
```

```
working index HEAD target         working index HEAD
----------------------------------------------------
 B       C     C    D     --soft   B       C     D
			  --mixed  B       D     D
			  --hard   D       D     D
			  --merge (disallowed)
			  --keep  (disallowed)
```

```
working index HEAD target         working index HEAD
----------------------------------------------------
 B       C     C    C     --soft   B       C     C
			  --mixed  B       C     C
			  --hard   C       C     C
			  --merge  B       C     C
			  --keep   B       C     C
```
