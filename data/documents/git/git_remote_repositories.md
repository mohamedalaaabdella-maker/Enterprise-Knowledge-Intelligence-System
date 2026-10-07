# Git Remote Repositories: clone, remote, fetch, pull, push

Source: Git Documentation
URL: https://git-scm.com/docs/git-remote
Version: 2.55.0
License: GPL-2.0-only (license of the original documentation; this file is an excerpt reformatted as Markdown)

## git clone

Clones a repository into a newly created directory, creates
remote-tracking branches for each branch in the cloned repository
(visible using `git branch --remotes`), and creates and checks out an
initial branch that is forked from the cloned repository's
currently active branch.

After the clone, a plain `git fetch` without arguments will update
all the remote-tracking branches, and a `git pull` without
arguments will in addition merge the remote master branch into the
current master branch, if any (this is untrue when `--single-branch`
is given; see below).

This default configuration is achieved by creating references to
the remote branch heads under `refs/remotes/origin` and
by initializing `remote.origin.url` and `remote.origin.fetch`
configuration variables.

## git remote

Manage the set of repositories ("remotes") whose branches you track.

### Selected git remote Commands

**`add`**

Add a remote named _<name>_ for the repository at
_<URL>_.  The command `git fetch <name>` can then be used to create and
update remote-tracking branches `<name>/<branch>`.

With `-f` option, `git fetch <name>` is run immediately after
the remote information is set up.

With `--tags` option, `git fetch <name>` imports every tag from the
remote repository.

With `--no-tags` option, `git fetch <name>` does not import tags from
the remote repository.

By default, only tags on fetched branches are imported
(see git-fetch(1)).

**`rename`**

Rename the remote named _<old>_ to _<new>_. All remote-tracking branches and
configuration settings for the remote are updated.

In case _<old>_ and _<new>_ are the same, and _<old>_ is a file under
`$GIT_DIR/remotes` or `$GIT_DIR/branches`, the remote is converted to
the configuration file format.

**`remove`**

**`rm`**

Remove the remote named _<name>_. All remote-tracking branches and
configuration settings for the remote are removed.

**`get-url`**

Retrieves the URLs for a remote. Configurations for `insteadOf` and
`pushInsteadOf` are expanded here. By default, only the first URL is listed.

With `--push`, push URLs are queried rather than fetch URLs.

With `--all`, all URLs for the remote will be listed.

**`set-url`**

Change URLs for the remote. Sets first URL for remote _<name>_ that matches
regex _<oldurl>_ (first URL if no _<oldurl>_ is given) to _<newurl>_. If
_<oldurl>_ doesn't match any URL, an error occurs and nothing is changed.

With `--push`, push URLs are manipulated instead of fetch URLs.

With `--add`, instead of changing existing URLs, new URL is added.

With `--delete`, instead of changing existing URLs, all URLs matching
regex _<URL>_ are deleted for remote _<name>_.  Trying to delete all
non-push URLs is an error.

**`show`**

Give some information about the remote _<name>_.

With `-n` option, the remote heads are not queried first with
`git ls-remote <name>`; cached information is used instead.

## git fetch

Fetch branches and/or tags (collectively, "refs") from one or more
other repositories, along with the objects necessary to complete their
histories.  Remote-tracking branches are updated (see the description
of _<refspec>_ below for ways to control this behavior).

By default, any tag that points into the histories being fetched is
also fetched; the effect is to fetch tags that
point at branches that you are interested in.  This default behavior
can be changed by using the `--tags` or `--no-tags` options or by
configuring `remote.<name>.tagOpt`.  By using a refspec that fetches tags
explicitly, you can fetch tags that do not point into branches you
are interested in as well.

`git fetch` can fetch from either a single named repository or URL,
or from several repositories at once if _<group>_ is given and
there is a `remotes.<group>` entry in the configuration file.
(See git-config(1)).

When no remote is specified, by default the `origin` remote will be used,
unless there's an upstream branch configured for the current branch.

The names of refs that are fetched, together with the object names
they point at, are written to `.git/FETCH_HEAD`.  This information
may be used by scripts or other git commands, such as git-pull(1).

## git pull

Integrate changes from a remote repository into the current branch.

First, `git pull` runs `git fetch` with the same arguments
(excluding merge options) to fetch remote branch(es).
Then it decides which remote branch to integrate: if you run `git pull`
with no arguments this defaults to the <<UPSTREAM-BRANCHES,upstream>>
for the current branch.
Then it integrates that branch into the current branch.

There are 4 main options for integrating the remote branch:

1. `git pull --ff-only` will only do "fast-forward" updates: it
   fails if your local branch has diverged from the remote branch.
   This is the default.
2. `git pull --rebase` runs `git rebase`
3. `git pull --no-rebase` runs `git merge`.
4. `git pull --squash` runs `git merge --squash`

You can also set the configuration options `pull.rebase`, `pull.squash`,
or `pull.ff` with your preferred behaviour.

If there's a merge conflict during the merge or rebase that you don't
want to handle, you can safely abort it with `git merge --abort` or
`git rebase --abort`.

## git push

Updates one or more branches, tags, or other references in one or more
remote repositories from your local repository, and sends all necessary
data that isn't already on the remote.

The simplest way to push is `git push <remote> <branch>`.
`git push origin main` will push the local `main` branch to the `main`
branch on the remote named `origin`.

You can also push to multiple remotes at once by using a remote group.
A remote group is a named list of remotes configured via `remotes.<name>`
in your git config:

$ git config remotes.all-remotes "origin gitlab backup"

Then `git push all-remotes` will push to `origin`, `gitlab`, and
`backup` in turn, as if you had run `git push` against each one
individually.  Each remote is pushed independently using its own
push mapping configuration. There is a `remotes.<group>` entry in
the configuration file. (See git-config(1)).

The `<repository>` argument defaults to the upstream for the current
branch, or `origin` if there's no configured upstream.

### Selected git push Options

**`-d`**

**`--delete`**

All listed refs are deleted from the remote repository. This is
the same as prefixing all refs with a colon.

**`-f`**

**`--force`**

Usually, `git push` will refuse to update a branch that is not an
ancestor of the commit being pushed.

This flag disables that check, the other safety checks in PUSH RULES
below, and the checks in `--force-with-lease`. It can cause the remote
repository to lose commits; use it with care.

**`-u`**

**`--set-upstream`**

For every branch that is up to date or successfully pushed, add
upstream (tracking) reference, used by argument-less
git-pull(1) and other commands. For more information,
see `branch.<name>.merge` in git-config(1).

### NOTE ABOUT FAST-FORWARDS

When an update changes a branch (or more in general, a ref) that used to
point at commit A to point at another commit B, it is called a
fast-forward update if and only if B is a descendant of A.

In a fast-forward update from A to B, the set of commits that the original
commit A built on top of is a subset of the commits the new commit B
builds on top of.  Hence, it does not lose any history.

In contrast, a non-fast-forward update will lose history.  For example,
suppose you and somebody else started at the same commit X, and you built
a history leading to commit B while the other person built a history
leading to commit A.  The history looks like this:

```

      B
     /
 ---X---A

```

Further suppose that the other person already pushed changes leading to A
back to the original repository from which you two obtained the original
commit X.

The push done by the other person updated the branch that used to point at
commit X to point at commit A.  It is a fast-forward.

But if you try to push, you will attempt to update the branch (that
now points at A) with commit B.  This does _not_ fast-forward.  If you did
so, the changes introduced by commit A will be lost, because everybody
will now start building on top of B.

The command by default does not allow an update that is not a fast-forward
to prevent such loss of history.
