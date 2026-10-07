# Dockerfile Reference

Source: Docker Documentation
URL: https://docs.docker.com/reference/dockerfile/
License: Apache-2.0 (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Overview

The Dockerfile supports the following instructions:

| Instruction                            | Description                                                 |
| :------------------------------------- | :---------------------------------------------------------- |
| `ADD`                          | Add local or remote files and directories.                  |
| `ARG`                          | Use build-time variables.                                   |
| `CMD`                          | Specify default commands.                                   |
| `COPY`                        | Copy files and directories.                                 |
| `ENTRYPOINT`            | Specify default executable.                                 |
| `ENV`                          | Set environment variables.                                  |
| `EXPOSE`                    | Describe which ports your application is listening on.      |
| `FROM`                        | Create a new build stage from a base image.                 |
| `HEALTHCHECK`          | Check a container's health on startup.                      |
| `LABEL`                      | Add metadata to an image.                                   |
| `MAINTAINER` | Specify the author of an image.                             |
| `ONBUILD`                  | Specify instructions for when the image is used in a build. |
| `RUN`                          | Execute build commands.                                     |
| `SHELL`                      | Set the default shell of an image.                          |
| `STOPSIGNAL`            | Specify the system call signal for exiting a container.     |
| `USER`                        | Set user and group ID.                                      |
| `VOLUME`                    | Create volume mounts.                                       |
| `WORKDIR`                  | Change working directory.                                   |

## Shell and exec form

The `RUN`, `CMD`, and `ENTRYPOINT` instructions all have two possible forms:

- `INSTRUCTION ["executable","param1","param2"]` (exec form)
- `INSTRUCTION command param1 param2` (shell form)

The exec form makes it possible to avoid shell string munging, and to invoke
commands using a specific command shell, or any other executable. It uses a
JSON array syntax, where each element in the array is a command, flag, or
argument.

The shell form is more relaxed, and emphasizes ease of use, flexibility, and
readability. The shell form automatically uses a command shell, whereas the
exec form does not.

### Exec form

The exec form is parsed as a JSON array, which means that
you must use double-quotes (") around words, not single-quotes (').

```dockerfile
ENTRYPOINT ["/bin/bash", "-c", "echo hello"]
```

The exec form is best used to specify an `ENTRYPOINT` instruction, combined
with `CMD` for setting default arguments that can be overridden at runtime. For
more information, see ENTRYPOINT.

#### Variable substitution

Using the exec form doesn't automatically invoke a command shell. This means
that normal shell processing, such as variable substitution, doesn't happen.
For example, `RUN [ "echo", "$HOME" ]` won't handle variable substitution for
`$HOME`.

## FROM

```dockerfile
FROM [--platform=<platform>] <image> [AS <name>]
```

Or

```dockerfile
FROM [--platform=<platform>] <image>[:<tag>] [AS <name>]
```

Or

```dockerfile
FROM [--platform=<platform>] <image>[@<digest>] [AS <name>]
```

The `FROM` instruction initializes a new build stage and sets the
base image for subsequent
instructions. As such, a valid Dockerfile must start with a `FROM` instruction.
The image can be any valid image.

- `ARG` is the only instruction that may precede `FROM` in the Dockerfile.
  See Understand how ARG and FROM interact.
- `FROM` can appear multiple times within a single Dockerfile to
  create multiple images or use one build stage as a dependency for another.
  Simply make a note of the last image ID output by the commit before each new
  `FROM` instruction. Each `FROM` instruction clears any state created by previous
  instructions.
- Optionally a name can be given to a new build stage by adding `AS name` to the
  `FROM` instruction. The name can be used in subsequent `FROM <name>`,
  `COPY --from=<name>`,
  and `RUN --mount=type=bind,from=<name>` instructions
  to refer to the image built in this stage.

## CMD

The `CMD` instruction sets the command to be executed when running a container
from an image.

You can specify `CMD` instructions using
shell or exec forms:

- `CMD ["executable","param1","param2"]` (exec form)
- `CMD ["param1","param2"]` (exec form, as default parameters to `ENTRYPOINT`)
- `CMD command param1 param2` (shell form)

There can only be one `CMD` instruction in a Dockerfile. If you list more than
one `CMD`, only the last one takes effect.

The purpose of a `CMD` is to provide defaults for an executing container. These
defaults can include an executable, or they can omit the executable, in which
case you must specify an `ENTRYPOINT` instruction as well.

If you would like your container to run the same executable every time, then
you should consider using `ENTRYPOINT` in combination with `CMD`. See
`ENTRYPOINT`. If the user specifies arguments to `docker run`
then they will override the default specified in `CMD`, but still use the
default `ENTRYPOINT`.

If `CMD` is used to provide default arguments for the `ENTRYPOINT` instruction,
both the `CMD` and `ENTRYPOINT` instructions should be specified in the
exec form.

> **Note**
> Don't confuse `RUN` with `CMD`. `RUN` actually runs a command and commits
> the result; `CMD` doesn't execute anything at build time, but specifies
> the intended command for the image.

## EXPOSE

```dockerfile
EXPOSE <port> [<port>/<protocol>...]
```

The `EXPOSE` instruction informs Docker that the container listens on the
specified network ports at runtime. You can specify whether the port listens on
TCP or UDP, and the default is TCP if you don't specify a protocol.

The `EXPOSE` instruction doesn't actually publish the port. It functions as a
type of documentation between the person who builds the image and the person who
runs the container, about which ports are intended to be published. To
publish the port when running the container, use the `-p` flag on `docker run`
to publish and map one or more ports, or the `-P` flag to publish all exposed
ports and map them to high-order ports.

By default, `EXPOSE` assumes TCP. You can also specify UDP:

```dockerfile
EXPOSE 80/udp
```

To expose on both TCP and UDP, include two lines:

```dockerfile
EXPOSE 80/tcp
EXPOSE 80/udp
```

In this case, if you use `-P` with `docker run`, the port will be exposed once
for TCP and once for UDP. Remember that `-P` uses an ephemeral high-ordered host
port on the host, so TCP and UDP doesn't use the same port.

Regardless of the `EXPOSE` settings, you can override them at runtime by using
the `-p` flag. For example

```console
$ docker run -p 80:80/tcp -p 80:80/udp ...
```

## COPY

COPY has two forms.
The latter form is required for paths containing whitespace.

```dockerfile
COPY [OPTIONS] <src> ... <dest>
COPY [OPTIONS] ["<src>", ... "<dest>"]
```

The available `[OPTIONS]` are:

| Option                             | Minimum Dockerfile version |
| ---------------------------------- | -------------------------- |
| `--from`           |                            |
| `--chmod`         | 1.2                        |
| `--chown`         |                            |
| `--link`           | 1.4                        |
| `--parents`     | 1.20                       |
| `--exclude`     | 1.19                       |

The `COPY` instruction copies new files or directories from `<src>` and adds
them to the filesystem of the image at the path `<dest>`. Files and directories
can be copied from the build context, build stage, named context, or an image.

The `ADD` and `COPY` instructions are functionally similar, but serve slightly different purposes.
Learn more about the differences between `ADD` and `COPY`.

## ENTRYPOINT

An `ENTRYPOINT` allows you to configure a container that will run as an executable.

`ENTRYPOINT` has two possible forms:

- The exec form, which is the preferred form:

  ```dockerfile
  ENTRYPOINT ["executable", "param1", "param2"]
  ```

- The shell form:

  ```dockerfile
  ENTRYPOINT command param1 param2
  ```

For more information about the different forms, see Shell and exec form.

The following command starts a container from the `nginx` with its default
content, listening on port 80:

```console
$ docker run -i -t --rm -p 80:80 nginx
```

Command line arguments to `docker run <image>` will be appended after all
elements in an exec form `ENTRYPOINT`, and will override all elements specified
using `CMD`.

This allows arguments to be passed to the entry point, i.e., `docker run
<image> -d` will pass the `-d` argument to the entry point. You can override
the `ENTRYPOINT` instruction using the `docker run --entrypoint` flag.

The shell form of `ENTRYPOINT` ignores any `CMD` or `docker run` command line
arguments. It also starts your `ENTRYPOINT` as a subcommand of `/bin/sh -c`,
which does not pass signals. This means that the executable will not be the
container's `PID 1`, and will not receive Unix signals. In this case, your
executable doesn't receive a `SIGTERM` from `docker stop <container>`.

Only the last `ENTRYPOINT` instruction in the Dockerfile will have an effect.

### Exec form ENTRYPOINT example

You can use the exec form of `ENTRYPOINT` to set fairly stable default commands
and arguments and then use `CMD` to set additional defaults that are more
likely to be changed.

## ENV

```dockerfile
ENV <key>=<value> [<key>=<value>...]
```

The `ENV` instruction sets the environment variable `<key>` to the value
`<value>`. This value will be in the environment for all subsequent instructions
in the build stage and can be replaced inline in
many as well. The value will be interpreted for other environment variables, so
quote characters will be removed if they are not escaped. Like command line parsing,
quotes and backslashes can be used to include spaces within values.

Example:

```dockerfile
ENV MY_NAME="John Doe"
ENV MY_DOG=Rex\ The\ Dog
ENV MY_CAT=fluffy
```

The `ENV` instruction allows for multiple `<key>=<value> ...` variables to be set
at one time, and the example below will yield the same net results in the final
image:

```dockerfile
ENV MY_NAME="John Doe" MY_DOG=Rex\ The\ Dog \
    MY_CAT=fluffy
```

The environment variables set using `ENV` will persist when a container is run
from the resulting image. You can view the values using `docker inspect`, and
change them using `docker run --env <key>=<value>`.
