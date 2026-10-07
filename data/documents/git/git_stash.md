# Git Stash

Source: Git Documentation
URL: https://git-scm.com/docs/git-stash
Version: 2.55.0
License: GPL-2.0-only (license of the original documentation; this file is an excerpt reformatted as Markdown)

## DESCRIPTION

Use `git stash` when you want to record the current state of the
working directory and the index, but want to go back to a clean
working directory.  The command saves your local modifications away
and reverts the working directory to match the `HEAD` commit.

The modifications stashed away by this command can be listed with
`git stash list`, inspected with `git stash show`, and restored
(potentially on top of a different commit) with `git stash apply`.
Calling `git stash` without any arguments is equivalent to `git stash push`.
A stash is by default listed as "WIP on *<branchname>* ...", but
you can give a more descriptive message on the command line when
you create one.

The latest stash you created is stored in `refs/stash`; older
stashes are found in the reflog of this reference and can be named using
the usual reflog syntax (e.g. `stash@{0}` is the most recently
created stash, `stash@{1}` is the one before it, `stash@{2.hours.ago}`
is also possible). Stashes may also be referenced by specifying just the
stash index (e.g. the integer `<n>` is equivalent to `stash@{<n>}`).

## COMMANDS

**`push [-p | --patch] [-S | --staged] [-k | --[no-]keep-index] [-u | --include-untracked] [ -a | --all] [-q | --quiet] [(-m|--message) <message>] [--pathspec-from-file=<file> [--pathspec-file-nul]] [--] [<pathspec>...]`**

Save your local modifications to a new *stash entry* and roll them
back to `HEAD` (in the working tree and in the index).
The _<message>_ part is optional and gives
the description along with the stashed state.

For quickly making a snapshot, you can omit "push".  In this mode,
pathspec elements are only allowed after a double hyphen `--`
to prevent a misspelled subcommand from making an unwanted stash entry.

**`save [-p | --patch] [-S | --staged] [-k | --[no-]keep-index] [-u | --include-untracked] [-a | --all] [-q | --quiet] [<message>]`**

This option is deprecated in favour of *git stash push*.  It
differs from "stash push" in that it cannot take pathspec.
Instead, all non-option arguments are concatenated to form the stash
message.

**`list [<log-options>]`**

List the stash entries that you currently have.  Each *stash entry* is
listed with its name (e.g. `stash@{0}` is the latest entry, `stash@{1}` is
the one before, etc.), the name of the branch that was current when the
entry was made, and a short description of the commit the entry was
based on.

```
stash@{0}: WIP on submit: 6ebd0e2... Update git-stash documentation
stash@{1}: On master: 9cc0589... Add git-stash
```

The command takes options applicable to the *git log*
command to control what is shown and how. See git-log(1).

**`show [-u | --include-untracked | --only-untracked] [<diff-options>] [<stash>]`**

Show the changes recorded in the stash entry as a diff between the
stashed contents and the commit back when the stash entry was first
created.
By default, the command shows the diffstat, but it will accept any
format known to *git diff* (e.g., `git stash show -p stash@{1}`
to view the second most recent entry in patch form).
If no _<diff-option>_ is provided, the default behavior will be given
by the `stash.showStat`, and `stash.showPatch` config variables. You
can also use `stash.showIncludeUntracked` to set whether
`--include-untracked` is enabled by default.

**`pop [--index] [-q | --quiet] [<stash>]`**

Remove a single stashed state from the stash list and apply it
on top of the current working tree state, i.e., do the inverse
operation of `git stash push`. The working directory must
match the index.

Applying the state can fail with conflicts; in this case, it is not
removed from the stash list. You need to resolve the conflicts by hand
and call `git stash drop` manually afterwards.

**`apply [--index] [-q | --quiet] [<stash>]`**

Like `pop`, but do not remove the state from the stash list. Unlike `pop`,
`<stash>` may be any commit that looks like a commit created by
`stash push` or `stash create`.

**`branch <branchname> [<stash>]`**

Creates and checks out a new branch named _<branchname>_ starting from
the commit at which the _<stash>_ was originally created, applies the
changes recorded in _<stash>_ to the new working tree and index.
If that succeeds, and _<stash>_ is a reference of the form
`stash@{<revision>}`, it then drops the _<stash>_.

This is useful if the branch on which you ran `git stash push` has
changed enough that `git stash apply` fails due to conflicts. Since
the stash entry is applied on top of the commit that was HEAD at the
time `git stash` was run, it restores the originally stashed state
with no conflicts.

**`clear`**

Remove all the stash entries. Note that those entries will then
be subject to pruning, and may be impossible to recover (see
*EXAMPLES* below for a possible strategy).

**`drop [-q | --quiet] [<stash>]`**

Remove a single stash entry from the list of stash entries.

**`create`**

Create a stash entry (which is a regular commit object) and
return its object name, without storing it anywhere in the ref
namespace.
This is intended to be useful for scripts.  It is probably not
the command you want to use; see "push" above.

## Selected Options

**`-u`**

**`--include-untracked`**

**`--no-include-untracked`**

When used with the `push` and `save` commands,
all untracked files are also stashed and then cleaned up with
`git clean`.

When used with the `show` command, show the untracked files in the stash
entry as part of the diff.

**`--index`**

This option is only valid for `pop` and `apply` commands.

Tries to reinstate not only the working tree's changes, but also
the index's ones. However, this can fail, when you have conflicts
(which are stored in the index, where you therefore can no longer
apply the changes as they were originally).

**`-k`**

**`--keep-index`**

**`--no-keep-index`**

This option is only valid for `push` and `save` commands.

All changes already added to the index are left intact.

## EXAMPLES

**Pulling into a dirty tree**

When you are in the middle of something, you learn that there are
upstream changes that are possibly relevant to what you are
doing.  When your local changes do not conflict with the changes in
the upstream, a simple `git pull` will let you move forward.

However, there are cases in which your local changes do conflict with
the upstream changes, and `git pull` refuses to overwrite your
changes.  In such a case, you can stash your changes away,
perform a pull, and then unstash, like this:

```
$ git pull
 ...
file foobar not up to date, cannot merge.
$ git stash
$ git pull
$ git stash pop
```

**Interrupted workflow**

When you are in the middle of something, your boss comes in and
demands that you fix something immediately.  Traditionally, you would
make a commit to a temporary branch to store your changes away, and
return to your original branch to make the emergency fix, like this:

```
# ... hack hack hack ...
$ git switch -c my_wip
$ git commit -a -m "WIP"
$ git switch master
$ edit emergency fix
$ git commit -a -m "Fix in a hurry"
$ git switch my_wip
$ git reset --soft HEAD^
# ... continue hacking ...
```

You can use *git stash* to simplify the above, like this:

```
# ... hack hack hack ...
$ git stash
$ edit emergency fix
$ git commit -a -m "Fix in a hurry"
$ git stash pop
# ... continue hacking ...
```

**Testing partial commits**
