# Git Rebasing

Source: Git Documentation
URL: https://git-scm.com/docs/git-rebase
Version: 2.55.0
License: GPL-2.0-only (license of the original documentation; this file is an excerpt reformatted as Markdown)

## DESCRIPTION

Transplant a series of commits onto a different starting point.
You can also use `git rebase` to reorder or combine commits: see INTERACTIVE
MODE below for how to do that.

For example, imagine that you have been working on the `topic` branch in this
history, and you want to "catch up" to the work done on the `master` branch.

```
          A---B---C topic
         /
    D---E---F---G master
```

You want to transplant the commits you made on `topic` since it diverged from
`master` (i.e. A, B, and C), on top of the current `master`.  You can do this
by running `git rebase master` while the `topic` branch is checked out.  If you
want to rebase `topic` while on another branch, `git rebase master topic` is a
shortcut for `git checkout topic && git rebase master`.

```
                  A'--B'--C' topic
                 /
    D---E---F---G master
```

If there is a merge conflict during this process, `git rebase` will stop at the
first problematic commit and leave conflict markers. If this happens, you can do
one of these things:

1. Resolve the conflict. You can use `git diff` to find the markers (<<<<<<)
   and make edits to resolve the conflict. For each file you edit, you need to
   tell Git that the conflict has been resolved. You can mark the conflict as
   resolved with  `git add <filename>`. After resolving all of the conflicts,
   you can continue the rebasing process with

   git rebase --continue

2. Stop the `git rebase` and return your branch to its original state with

   git rebase --abort

3. Skip the commit that caused the merge conflict with

   git rebase --skip

If you don't specify an `<upstream>` to rebase onto, the upstream configured in
`branch.<name>.remote` and `branch.<name>.merge` options will be used (see
git-config(1) for details) and the `--fork-point` option is
assumed.  If you are currently not on any branch or if the current
branch does not have a configured upstream, the rebase will abort.

Here is a simplified description of what `git rebase <upstream>` does:

1. Make a list of all commits on your current branch since it branched
   off from `<upstream>` that do not have an equivalent commit in
   `<upstream>`.
2. Check out `<upstream>` with the equivalent of
   `git checkout --detach <upstream>`.
3. Replay the commits, one by one, in order. This is similar to running
   `git cherry-pick <commit>` for each commit. See REBASING MERGES for how merges
   are handled.
4. Update your branch to point to the final commit with the equivalent
   of `git checkout -B <branch>`.

**Note:**
When starting the rebase, `ORIG_HEAD` is set to point to the commit at the tip
of the to-be-rebased branch. However, `ORIG_HEAD` is not guaranteed to still
point to that commit at the end of the rebase if other commands that change
`ORIG_HEAD` (like `git reset`) are used during the rebase. The previous branch
tip, however, is accessible using the reflog of the current branch (i.e. `@{1}`,
see gitrevisions(7)).

## TRANSPLANTING A TOPIC BRANCH WITH --ONTO

Here is how you would transplant a topic branch based on one
branch to another, to pretend that you forked the topic branch
from the latter branch, using `rebase --onto`.

First let's assume your *topic* is based on branch *next*.
For example, a feature developed in *topic* depends on some
functionality which is found in *next*.

```
    o---o---o---o---o  master
         \
          o---o---o---o---o  next
                           \
                            o---o---o  topic
```

We want to make *topic* forked from branch *master*; for example,
because the functionality on which *topic* depends was merged into the
more stable *master* branch. We want our tree to look like this:

```
    o---o---o---o---o  master
        |            \
        |             o'--o'--o'  topic
         \
          o---o---o---o---o  next
```

We can get this using the following command:

    git rebase --onto master next topic

Another example of --onto option is to rebase part of a
branch.  If we have the following situation:

```
                            H---I---J topicB
                           /
                  E---F---G  topicA
                 /
    A---B---C---D  master
```

then the command

    git rebase --onto master topicA topicB

would result in:

```
                 H'--I'--J'  topicB
                /
                | E---F---G  topicA
                |/
    A---B---C---D  master
```

This is useful when topicB does not depend on topicA.

A range of commits could also be removed with rebase.  If we have
the following situation:

```
    E---F---G---H---I---J  topicA
```

then the command

    git rebase --onto topicA~5 topicA~3 topicA

would result in the removal of commits F and G:

```
    E---H'---I'---J'  topicA
```

This is useful if F and G were flawed in some way, or should not be
part of topicA.  Note that the argument to `--onto` and the `<upstream>`
parameter can be any valid commit-ish.

## MODE OPTIONS

The options in this section cannot be used with any other option,
including not with each other:

**--continue**

Restart the rebasing process after having resolved a merge conflict.

**--skip**

Restart the rebasing process by skipping the current patch.

**--abort**

Abort the rebase operation and reset HEAD to the original
branch. If `<branch>` was provided when the rebase operation was
started, then `HEAD` will be reset to `<branch>`. Otherwise `HEAD`
will be reset to where it was when the rebase operation was
started.

**--quit**

Abort the rebase operation but `HEAD` is not reset back to the
original branch. The index and working tree are also left
unchanged as a result. If a temporary stash entry was created
using `--autostash`, it will be saved to the stash list.

**--edit-todo**

Edit the todo list during an interactive rebase.

**--show-current-patch**

Show the current patch in an interactive rebase or when rebase
is stopped because of conflicts. This is the equivalent of
`git show REBASE_HEAD`.

## Selected Options

**--onto <newbase>**

Starting point at which to create the new commits. If the
`--onto` option is not specified, the starting point is
`<upstream>`.  May be any valid commit, and not just an
existing branch name.

As a special case, you may use "A\...B" as a shortcut for the
merge base of A and B if there is exactly one merge base. You can
leave out at most one of A and B, in which case it defaults to HEAD.

See TRANSPLANTING A TOPIC BRANCH WITH --ONTO above for examples.

**-i**

**--interactive**

Make a list of the commits which are about to be rebased.  Let the
user edit that list before rebasing.  This mode can also be used to
split commits (see SPLITTING COMMITS below).

The commit list format can be changed by setting the configuration option
rebase.instructionFormat.  A customized instruction format will automatically
have the commit hash prepended to the format.

See also INCOMPATIBLE OPTIONS below.

## INTERACTIVE MODE

Rebasing interactively means that you have a chance to edit the commits
which are rebased.  You can reorder the commits, and you can
remove them (weeding out bad or otherwise unwanted patches).

The interactive mode is meant for this type of workflow:

1. have a wonderful idea
2. hack on the code
3. prepare a series for submission
4. submit

where point 2. consists of several instances of

a) regular use

 1. finish something worthy of a commit
 2. commit

b) independent fixup

 1. realize that something does not work
 2. fix that
 3. commit it

Sometimes the thing fixed in b.2. cannot be amended to the not-quite
perfect commit it fixes, because that commit is buried deeply in a
patch series.  That is exactly what interactive rebase is for: use it
after plenty of "a"s and "b"s, by rearranging and editing
commits, and squashing multiple commits into one.

Start it with the last commit you want to retain as-is:

git rebase -i <after-this-commit>

An editor will be fired up with all the commits in your current branch
(ignoring merge commits), which come after the given commit.  You can
reorder the commits in this list to your heart's content, and you can
remove them.  The list looks more or less like this:

```
pick deadbee The oneline of this commit
pick fa1afe1 The oneline of the next commit
...
```

The oneline descriptions are purely for your pleasure; *git rebase* will
not look at them but at the commit names ("deadbee" and "fa1afe1" in this
example), so do not delete or edit the names.

By replacing the command "pick" with the command "edit", you can tell
`git rebase` to stop after applying that commit, so that you can edit
the files and/or the commit message, amend the commit, and continue
rebasing.

To interrupt the rebase (just like an "edit" command would do, but without
cherry-picking any commit first), use the "break" command.

## RECOVERING FROM UPSTREAM REBASE

Rebasing (or any other form of rewriting) a branch that others have
based work on is a bad idea: anyone downstream of it is forced to
manually fix their history.  This section explains how to do the fix
from the downstream's point of view.  The real fix, however, would be
to avoid rebasing the upstream in the first place.

To illustrate, suppose you are in a situation where someone develops a
*subsystem* branch, and you are working on a *topic* that is dependent
on this *subsystem*.  You might end up with a history like the
following:

```
    o---o---o---o---o---o---o---o  master
	 \
	  o---o---o---o---o  subsystem
			   \
			    *---*---*  topic
```

If *subsystem* is rebased against *master*, the following happens:

```
    o---o---o---o---o---o---o---o  master
	 \			 \
	  o---o---o---o---o	  o'--o'--o'--o'--o'  subsystem
			   \
			    *---*---*  topic
```

If you now continue development as usual, and eventually merge *topic*
to *subsystem*, the commits from *subsystem* will remain duplicated forever:

```
    o---o---o---o---o---o---o---o  master
	 \			 \
	  o---o---o---o---o	  o'--o'--o'--o'--o'--M	 subsystem
			   \			     /
			    *---*---*-..........-*--*  topic
```

Such duplicates are generally frowned upon because they clutter up
history, making it harder to follow.  To clean things up, you need to
transplant the commits on *topic* to the new *subsystem* tip, i.e.,
rebase *topic*.  This becomes a ripple effect: anyone downstream from
*topic* is forced to rebase too, and so on!

There are two kinds of fixes, discussed in the following subsections:

**Easy case: The changes are literally the same.**

This happens if the *subsystem* rebase was a simple rebase and
had no conflicts.

**Hard case: The changes are not the same.**
