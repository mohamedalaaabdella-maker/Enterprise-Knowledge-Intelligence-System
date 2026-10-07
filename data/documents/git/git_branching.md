# Git Branching

Source: Git Documentation
URL: https://git-scm.com/docs/git-branch
Version: 2.55.0
License: GPL-2.0-only (license of the original documentation; this file is an excerpt reformatted as Markdown)

## git branch

If `--list` is given, or if there are no non-option arguments, existing
branches are listed; the current branch will be highlighted in green and
marked with an asterisk.  Any branches checked out in linked worktrees will
be highlighted in cyan and marked with a plus sign. Option `-r` causes the
remote-tracking branches to be listed,
and option `-a` shows both local and remote branches.

If a `<pattern>`
is given, it is used as a shell wildcard to restrict the output to
matching branches. If multiple patterns are given, a branch is shown if
it matches any of the patterns.

Note that when providing a
`<pattern>`, you must use `--list`; otherwise the command may be interpreted
as branch creation.

With `--contains`, shows only the branches that contain the named commit
(in other words, the branches whose tip commits are descendants of the
named commit), `--no-contains` inverts it. With `--merged`, only branches
merged into the named commit (i.e. the branches whose tip commits are
reachable from the named commit) will be listed.  With `--no-merged` only
branches not merged into the named commit will be listed.  If the _<commit>_
argument is missing it defaults to `HEAD` (i.e. the tip of the current
branch).

The command's second form creates a new branch head named _<branch-name>_
which points to the current `HEAD`, or _<start-point>_ if given. As a
special case, for _<start-point>_, you may use `<rev-A>...<rev-B>` as a
shortcut for the merge base of _<rev-A>_ and _<rev-B>_ if there is exactly
one merge base. You can leave out at most one of _<rev-A>_ and _<rev-B>_,
in which case it defaults to `HEAD`.

Note that this will create the new branch, but it will not switch the
working tree to it; use `git switch <new-branch>` to switch to the
new branch.

When a local branch is started off a remote-tracking branch, Git sets up the
branch (specifically the `branch.<name>.remote` and `branch.<name>.merge`
configuration entries) so that `git pull` will appropriately merge from
the remote-tracking branch. This behavior may be changed via the global
`branch.autoSetupMerge` configuration flag. That setting can be
overridden by using the `--track` and `--no-track` options, and
changed later using `git branch --set-upstream-to`.

With a `-m` or `-M` option, _<old-branch>_ will be renamed to _<new-branch>_.
If _<old-branch>_ had a corresponding reflog, it is renamed to match
_<new-branch>_, and a reflog entry is created to remember the branch
renaming. If _<new-branch>_ exists, `-M` must be used to force the rename
to happen.

The `-c` and `-C` options have the exact same semantics as `-m` and
`-M`, except instead of the branch being renamed, it will be copied to a
new name, along with its config and reflog.

With a `-d` or `-D` option, _<branch-name>_ will be deleted.  You may
specify more than one branch for deletion.  If the branch currently
has a reflog then the reflog will also be deleted.

Use `-r` together with `-d` to delete remote-tracking branches. Note, that it
only makes sense to delete remote-tracking branches if they no longer exist
in the remote repository or if `git fetch` was configured not to fetch
them again. See also the `prune` subcommand of git-remote(1) for a
way to clean up all obsolete remote-tracking branches.

## Selected git branch Options

**`-d`**

**`--delete`**

Delete a branch. The branch must be fully merged in its
upstream branch, or in `HEAD` if no upstream was set with
`--track` or `--set-upstream-to`.

**`-D`**

Shortcut for `--delete --force`.

**`-m`**

**`--move`**

Move/rename a branch, together with its config and reflog.

**`-M`**

Shortcut for `--move --force`.

**`-r`**

**`--remotes`**

List or delete (if used with `-d`) the remote-tracking branches.
Combine with `--list` to match the optional pattern(s).

**`-a`**

**`--all`**

List both remote-tracking branches and local branches.
Combine with `--list` to match optional pattern(s).

**`-l`**

**`--list`**

List branches.  With optional `<pattern>...`, e.g. `git
branch --list *maint-**`, list only the branches that match
the pattern(s).

**`--show-current`**

Print the name of the current branch. In detached `HEAD` state,
nothing is printed.

**`-u <upstream>`**

**`--set-upstream-to=<upstream>`**

Set up _<branch-name>_'s tracking information so _<upstream>_ is
considered _<branch-name>_'s upstream branch. If no _<branch-name>_
is specified, then it defaults to the current branch.

**`--merged [<commit>]`**

Only list branches whose tips are reachable from
_<commit>_ (`HEAD` if not specified). Implies `--list`.

**`--no-merged [<commit>]`**

Only list branches whose tips are not reachable from
_<commit>_ (`HEAD` if not specified). Implies `--list`.

## git branch Examples

**Start development from a known tag**

```
$ git clone git://git.kernel.org/pub/scm/.../linux-2.6 my2.6
$ cd my2.6
$ git branch my2.6.14 v2.6.14   <1>
$ git switch my2.6.14
```

<1> This step and the next one could be combined into a single step with
    "checkout -b my2.6.14 v2.6.14".

**Delete an unneeded branch**

```
$ git clone git://git.kernel.org/.../git.git my.git
$ cd my.git
$ git branch -d -r origin/todo origin/html origin/man   <1>
$ git branch -D test                                    <2>
```

<1> Delete the remote-tracking branches "todo", "html" and "man". The next
    `git fetch` or `git pull` will create them again unless you configure them not to.
    See git-fetch(1).
<2> Delete the "test" branch even if the "master" branch (or whichever branch
    is currently checked out) does not have all commits from the test branch.

**Listing branches from a specific remote**

```
$ git branch -r -l '<remote>/<pattern>'                 <1>
$ git for-each-ref 'refs/remotes/<remote>/<pattern>'    <2>
```

<1> Using `-a` would conflate _<remote>_ with any local branches you happen to
    have been prefixed with the same _<remote>_ pattern.
<2> `for-each-ref` can take a wide range of options. See git-for-each-ref(1)

Patterns will normally need quoting.

## git switch

Switch to a specified branch. The working tree and the index are
updated to match the branch. All new commits will be added to the tip
of this branch.

Optionally a new branch could be created with either `-c`, `-C`,
automatically from a remote branch of same name (see `--guess`), or
detach the working tree from any branch with `--detach`, along with
switching.

Switching branches does not require a clean index and working tree
(i.e. no differences compared to `HEAD`). The operation is aborted
however if the operation leads to loss of local changes, unless told
otherwise with `--discard-changes` or `--merge`.

### Selected git switch Options

**`-c <new-branch>`**

**`--create <new-branch>`**

Create a new branch named _<new-branch>_ starting at
_<start-point>_ before switching to the branch. This is the
transactional equivalent of

```
$ git branch <new-branch>
$ git switch <new-branch>
```

that is to say, the branch is not reset/created unless `git switch` is
successful (e.g., when the branch is in use in another worktree, not
just the current branch stays the same, but the branch is not reset to
the start-point, either).

**`-C <new-branch>`**

**`--force-create <new-branch>`**

Similar to `--create` except that if _<new-branch>_ already
exists, it will be reset to _<start-point>_. This is a
convenient shortcut for:

```
$ git branch -f _<new-branch>_
$ git switch _<new-branch>_
```

**`-d`**

**`--detach`**

Switch to a commit for inspection and discardable
experiments. See the "DETACHED HEAD" section in
git-checkout(1) for details.

**`--discard-changes`**

Proceed even if the index or the working tree differs from
`HEAD`. Both the index and working tree are restored to match
the switching target. If `--recurse-submodules` is specified,
submodule content is also restored to match the switching
target. This is used to throw away local changes.

### EXAMPLES

The following command switches to the "master" branch:

```
$ git switch master
```

After working in the wrong branch, switching to the correct branch
would be done using:

```
$ git switch mytopic
```

However, your "wrong" branch and correct "mytopic" branch may differ
in files that you have modified locally, in which case the above
switch would fail like this:

```
$ git switch mytopic
error: You have local changes to 'frotz'; not switching branches.
```

You can give the `-m` flag to the command, which will carry your local
changes to the new branch:

```
$ git switch -m mytopic
Applied autostash.
Switched to branch 'mytopic'
The following paths have local changes:
M	frotz
```

After the switch, the local modifications are reapplied and are _not_
registered in your index file, so `git diff` would show you what
changes you made since the tip of the new branch.

To switch back to the previous branch before we switched to mytopic
(i.e. "master" branch):

```
$ git switch -
```
