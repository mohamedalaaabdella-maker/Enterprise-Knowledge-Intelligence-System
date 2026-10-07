# Git Repository Basics

Source: Git Documentation
URL: https://git-scm.com/docs/gittutorial
Version: 2.55.0
License: GPL-2.0-only (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Overview (from gittutorial)

This tutorial explains how to import a new project into Git, make
changes to it, and share changes with other developers.

If you are instead primarily interested in using Git to fetch a project,
for example, to test the latest version, you may prefer to start with
the first two chapters of The Git User's Manual.

First, note that you can get documentation for a command such as
`git log --graph` with:

```
$ man git-log
```

or:

```
$ git help log
```

With the latter, you can use the manual viewer of your choice; see
git-help(1) for more information.

It is a good idea to introduce yourself to Git with your name and
public email address before doing any operation.  The easiest
way to do so is:

```
$ git config --global user.name "Your Name Comes Here"
$ git config --global user.email you@yourdomain.example.com
```

## Importing a new project

Assume you have a tarball `project.tar.gz` with your initial work.  You
can place it under Git revision control as follows.

```
$ tar xzf project.tar.gz
$ cd project
$ git init
```

Git will reply

```
Initialized empty Git repository in .git/
```

You've now initialized the working directory--you may notice a new
directory created, named `.git`.

Next, tell Git to take a snapshot of the contents of all files under the
current directory (note the `.`), with `git add`:

```
$ git add .
```

This snapshot is now stored in a temporary staging area which Git calls
the "index".  You can permanently store the contents of the index in the
repository with `git commit`:

```
$ git commit
```

This will prompt you for a commit message.  You've now stored the first
version of your project in Git.

## Making changes

Modify some files, then add their updated contents to the index:

```
$ git add file1 file2 file3
```

You are now ready to commit.  You can see what is about to be committed
using `git diff` with the `--cached` option:

```
$ git diff --cached
```

(Without `--cached`, `git diff` will show you any changes that
you've made but not yet added to the index.)  You can also get a brief
summary of the situation with `git status`:

```
$ git status
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)

	modified:   file1
	modified:   file2
	modified:   file3

```

If you need to make any further adjustments, do so now, and then add any
newly modified content to the index.  Finally, commit your changes with:

```
$ git commit
```

This will again prompt you for a message describing the change, and then
record a new version of the project.

Alternatively, instead of running `git add` beforehand, you can use

```
$ git commit -a
```

which will automatically notice any modified (but not new) files, add
them to the index, and commit, all in one step.

A note on commit messages: Though not required, it's a good idea to
begin the commit message with a single short (no more than 50
characters) line summarizing the change, followed by a blank line and
then a more thorough description. The text up to the first blank line in
a commit message is treated as the commit title, and that title is used
throughout Git.  For example, git-format-patch(1) turns a
commit into email, and it uses the title on the Subject line and the
rest of the commit in the body.

## Git tracks content not files

Many revision control systems provide an `add` command that tells the
system to start tracking changes to a new file.  Git's `add` command
does something simpler and more powerful: `git add` is used both for new
and newly modified files, and in both cases it takes a snapshot of the
given files and stages that content in the index, ready for inclusion in
the next commit.

## Viewing project history

At any point you can view the history of your changes using

```
$ git log
```

If you also want to see complete diffs at each step, use

```
$ git log -p
```

Often the overview of the change is useful to get a feel of
each step

```
$ git log --stat --summary
```

## git init

This command creates an empty Git repository - basically a `.git`
directory with subdirectories for `objects`, `refs/heads`,
`refs/tags`, and template files.  An initial branch without any
commits will be created (see the `--initial-branch` option below
for its name).

If the `GIT_DIR` environment variable is set then it specifies a path
to use instead of `./.git` for the base of the repository.

If the object storage directory is specified via the
`GIT_OBJECT_DIRECTORY` environment variable then the sha1 directories
are created underneath; otherwise, the default `$GIT_DIR/objects`
directory is used.

Running `git init` in an existing repository is safe. It will not
overwrite things that are already there. The primary reason for
rerunning `git init` is to pick up newly added templates (or to move
the repository to another place if `--separate-git-dir` is given).

### Selected git init Options

**`--bare`**

Create a bare repository. If `GIT_DIR` environment is not set, it is set to the
current working directory.

**`-b <branch-name>`**

**`--initial-branch=<branch-name>`**

Use _<branch-name>_ for the initial branch in the newly created
repository.  If not specified, fall back to the default name
(currently `master`, but this will change to `main` when Git 3.0 is released).
The default name can be customized via the `init.defaultBranch` configuration
variable.
