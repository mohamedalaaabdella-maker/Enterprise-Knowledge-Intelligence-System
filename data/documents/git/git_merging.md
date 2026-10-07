# Git Merging

Source: Git Documentation
URL: https://git-scm.com/docs/git-merge
Version: 2.55.0
License: GPL-2.0-only (license of the original documentation; this file is an excerpt reformatted as Markdown)

## DESCRIPTION

Incorporates changes from the named commits (since the time their
histories diverged from the current branch) into the current
branch.  This command is used by `git pull` to incorporate changes
from another repository and can be used by hand to merge changes
from one branch into another.

Assume the following history exists and the current branch is
`master`:

```
          A---B---C topic
         /
    D---E---F---G master
```

Then `git merge topic` will replay the changes made on the
`topic` branch since it diverged from `master` (i.e., `E`) until
its current commit (`C`) on top of `master`, and record the result
in a new commit along with the names of the two parent commits and
a log message from the user describing the changes. Before the operation,
`ORIG_HEAD` is set to the tip of the current branch (`G`).

```
          A---B---C topic
         /         \
    D---E---F---G---H master
```

A merge stops if there's a conflict that cannot be resolved
automatically or if `--no-commit` was provided when initiating the
merge. At that point you can run `git merge --abort` or `git merge
--continue`.

`git merge --abort` will abort the merge process and try to reconstruct
the pre-merge state. However, if there were uncommitted changes when the
merge started (and especially if those changes were further modified
after the merge was started), `git merge --abort` will in some cases be
unable to reconstruct the original (pre-merge) changes. Therefore:

> **Warning:** Running `git merge` with non-trivial uncommitted changes is
discouraged: while possible, it may leave you in a state that is hard to
back out of in the case of a conflict.

## FAST-FORWARD MERGE

Often the current branch head is an ancestor of the named commit.
This is the most common case especially when invoked from `git
pull`: you are tracking an upstream repository, you have committed
no local changes, and now you want to update to a newer upstream
revision.  In this case, a new commit is not needed to store the
combined history; instead, the `HEAD` (along with the index) is
updated to point at the named commit, without creating an extra
merge commit.

This behavior can be suppressed with the `--no-ff` option.

## TRUE MERGE

Except in a fast-forward merge (see above), the branches to be
merged must be tied together by a merge commit that has both of them
as its parents.

A merged version reconciling the changes from all branches to be
merged is committed, and your `HEAD`, index, and working tree are
updated to it.  It is possible to have modifications in the working
tree as long as they do not overlap; the update will preserve them.

When it is not obvious how to reconcile the changes, the following
happens:

1. The `HEAD` pointer stays the same.
2. The `MERGE_HEAD` ref is set to point to the other branch head.
3. Paths that merged cleanly are updated both in the index file and
   in your working tree.
4. For conflicting paths, the index file records up to three
   versions: stage 1 stores the version from the common ancestor,
   stage 2 from `HEAD`, and stage 3 from `MERGE_HEAD` (you
   can inspect the stages with `git ls-files -u`).  The working
   tree files contain the result of the merge operation; i.e. 3-way
   merge results with familiar conflict markers `<<<` `===` `>>>`.
5. A ref named `AUTO_MERGE` is written, pointing to a tree
   corresponding to the current content of the working tree (including
   conflict markers for textual conflicts).  Note that this ref is only
   written when the `ort` merge strategy is used (the default).
6. No other changes are made.  In particular, the local
   modifications you had before you started merge will stay the
   same and the index entries for them stay as they were,
   i.e. matching `HEAD`.

If you tried a merge which resulted in complex conflicts and
want to start over, you can recover with `git merge --abort`.

## Selected Options

**`--ff`**

**`--no-ff`**

**`--ff-only`**

Specifies how a merge is handled when the merged-in history is
already a descendant of the current history.  `--ff` is the
default unless merging an annotated (and possibly signed) tag
that is not stored in its natural place in the `refs/tags/`
hierarchy, in which case `--no-ff` is assumed.

With `--ff`, when possible resolve the merge as a fast-forward (only
update the branch pointer to match the merged branch; do not create a
merge commit).  When not possible (when the merged-in history is not a
descendant of the current history), create a merge commit.

With `--no-ff`, create a merge commit in all cases, even when the merge
could instead be resolved as a fast-forward.

With `--ff-only`, resolve the merge as a fast-forward when possible.
When not possible, refuse to merge and exit with a non-zero status.

**`--squash`**

**`--no-squash`**

Produce the working tree and index state as if a real merge
happened (except for the merge information), but do not actually
make a commit, move the `HEAD`, or record `$GIT_DIR/MERGE_HEAD`
(to cause the next `git commit` command to create a merge
commit).  This allows you to create a single commit on top of
the current branch whose effect is the same as merging another
branch (or more in case of an octopus).

With `--no-squash` perform the merge and commit the result. This
option can be used to override `--squash`.

With `--squash`, `--commit` is not allowed, and will fail.

**`--abort`**

Abort the current conflict resolution process, and
try to reconstruct the pre-merge state. If an autostash entry is
present, apply it to the worktree.

If there were uncommitted worktree changes present when the merge
started, `git merge --abort` will in some cases be unable to
reconstruct these changes. It is therefore recommended to always
commit or stash your changes before running `git merge`.

`git merge --abort` is equivalent to `git reset --merge` when
`MERGE_HEAD` is present unless `MERGE_AUTOSTASH` is also present in
which case `git merge --abort` applies the stash entry to the worktree
whereas `git reset --merge` will save the stashed changes in the stash
list.

**`--continue`**

After a `git merge` stops due to conflicts you can conclude the
merge by running `git merge --continue` (see "HOW TO RESOLVE
CONFLICTS" section below).

## HOW CONFLICTS ARE PRESENTED

During a merge, the working tree files are updated to reflect the result
of the merge.  Among the changes made to the common ancestor's version,
non-overlapping ones (that is, you changed an area of the file while the
other side left that area intact, or vice versa) are incorporated in the
final result verbatim.  When both sides made changes to the same area,
however, Git cannot randomly pick one side over the other, and asks you to
resolve it by leaving what both sides did to that area.

By default, Git uses the same style as the one used by the "merge" program
from the RCS suite to present such a conflicted hunk, like this:

```
Here are lines that are either unchanged from the common
ancestor, or cleanly resolved because only one side changed,
or cleanly resolved because both sides changed the same way.
<<<<<<< yours:sample.txt
Conflict resolution is hard;
let's go shopping.
=======
Git makes conflict resolution easy.
>>>>>>> theirs:sample.txt
And here is another line that is cleanly resolved or unmodified.
```

The area where a pair of conflicting changes happened is marked with markers
`<<<<<<<`, `=======`, and `>>>>>>>`.  The part before the `=======`
is typically your side, and the part afterwards is typically their side.

The default format does not show what the original said in the conflicting
area.  You cannot tell how many lines are deleted and replaced with
Barbie's remark on your side.  The only thing you can tell is that your
side wants to say it is hard and you'd prefer to go shopping, while the
other side wants to claim it is easy.

## HOW TO RESOLVE CONFLICTS

After seeing a conflict, you can do two things:

 * Decide not to merge.  The only clean-ups you need are to reset
   the index file to the `HEAD` commit to reverse 2. and to clean
   up working tree changes made by 2. and 3.; `git merge --abort`
   can be used for this.

 * Resolve the conflicts.  Git will mark the conflicts in
   the working tree.  Edit the files into shape and
   `git add` them to the index.  Use `git commit` or
   `git merge --continue` to seal the deal. The latter command
   checks whether there is a (interrupted) merge in progress
   before calling `git commit`.

You can work through the conflict with a number of tools:

 * Use a mergetool.  `git mergetool` to launch a graphical
   mergetool which will work through the merge with you.

 * Look at the diffs.  `git diff` will show a three-way diff,
   highlighting changes from both the `HEAD` and `MERGE_HEAD`
   versions. `git diff AUTO_MERGE` will show what changes you've
   made so far to resolve textual conflicts.

 * Look at the diffs from each branch. `git log --merge -p <path>`
   will show diffs first for the `HEAD` version and then the
   `MERGE_HEAD` version.

 * Look at the originals.  `git show :1:filename` shows the
   common ancestor, `git show :2:filename` shows the `HEAD`
   version, and `git show :3:filename` shows the `MERGE_HEAD`
   version.
