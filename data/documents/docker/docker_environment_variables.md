# Docker Environment Variables

Source: Docker Documentation
URL: https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/
License: Apache-2.0 (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Setting Environment Variables with docker run

This option sets an environment variable `foo` inside the container with the value `bar`.

```console
$ docker run -e foo=bar postgres env
```

You will see output like the following:

```console
HOSTNAME=2042f2e6ebe4
foo=bar
```

> **Tip**
>
> The `.env` file acts as a convenient way to set environment variables for your Docker containers without cluttering your command line with numerous `-e` flags. To use a `.env` file, you can pass `--env-file` option with the `docker run` command.
> ```console
> $ docker run --env-file .env postgres env
> ```

## Use the environment attribute

You can set environment variables directly in your container's environment with the
`environment` attribute in your `compose.yaml`.

It supports both list and mapping syntax:

```yaml
services:
  webapp:
    environment:
      DEBUG: "true"
```
is equivalent to
```yaml
services:
  webapp:
    environment:
      - DEBUG=true
```

See `environment` attribute for more examples on how to use it.

### Additional information

- You can choose not to set a value and pass the environment variables from your shell straight through to your containers. It works in the same way as `docker run -e VARIABLE ...`:
  ```yaml
  web:
    environment:
      - DEBUG
  ```
The value of the `DEBUG` variable in the container is taken from the value for the same variable in the shell in which Compose is run. Note that in this case no warning is issued if the `DEBUG` variable in the shell environment is not set.

- You can also take advantage of interpolation. In the following example, the result is similar to the one above but Compose gives you a warning if the `DEBUG` variable is not set in the shell environment or in an `.env` file in the project directory.

  ```yaml
  web:
    environment:
      - DEBUG=${DEBUG}
  ```

## Use the env_file attribute

A container's environment can also be set using `.env` files along with the `env_file` attribute.

```yaml
services:
  webapp:
    env_file: "webapp.env"
```

Using an `.env` file lets you use the same file for use by a plain `docker run --env-file ...` command, or to share the same `.env` file within multiple services without the need to duplicate a long `environment` YAML block.

It can also help you keep your environment variables separate from your main configuration file, providing a more organized and secure way to manage sensitive information, as you do not need to place your `.env` file in the root of your project's directory.

The `env_file` attribute also lets you use multiple `.env` files in your Compose application.

The paths to your `.env` file, specified in the `env_file` attribute, are relative to the location of your `compose.yaml` file.

> **Important**
>
> Interpolation in `.env` files is a Docker Compose CLI feature.
>
> It is not supported when running `docker run --env-file ...`.

### Additional information

- If multiple files are specified, they are evaluated in order and can override values set in previous files.
- As of Docker Compose version 2.24.0, you can set your `.env` file, defined by the `env_file` attribute, to be optional by using the `required` field. When `required` is set to `false` and the `.env` file is missing, Compose silently ignores the entry.
  ```yaml
  env_file:
    - path: ./default.env
      required: true # default
    - path: ./override.env
      required: false
  ```
- As of Docker Compose version 2.30.0, you can use an alternative file format for the `env_file` with the `format` attribute. For more information, see `format`.
- Values in your `.env` file can be overridden from the command line by using `docker compose run -e`.

## Set environment variables with docker compose run --env

Similar to `docker run --env`, you can set environment variables temporarily with `docker compose run --env` or its short form `docker compose run -e`:

```console
$ docker compose run -e DEBUG=1 web python console.py
```

### Additional information

- You can also pass a variable from the shell or your environment files by not giving it a value:

  ```console
  $ docker compose run -e DEBUG web python console.py
  ```

The value of the `DEBUG` variable in the container is taken from the value for the same variable in the shell in which Compose is run or from the environment files.

## Environment Variable Precedence in Compose

In the following example, a different value for the same environment variable in an `.env` file and with the `environment` attribute in the Compose file:

```console
$ cat ./webapp.env
NODE_ENV=test

$ cat compose.yaml
services:
  webapp:
    image: 'webapp'
    env_file:
     - ./webapp.env
    environment:
     - NODE_ENV=production
```

The environment variable defined with the `environment` attribute takes precedence.

```console
$ docker compose run webapp env | grep NODE_ENV
NODE_ENV=production
```

The following table uses `VALUE`, an environment variable defining the version for an image, as an example.

### How the table works

Each column represents a context from where you can set a value, or substitute in a value for `VALUE`.

The columns `Host OS environment` and `.env` file is listed only for illustration purposes. In reality, they don't result in a variable in the container by itself, but in conjunction with either the `environment` or `env_file` attribute.

Each row represents a combination of contexts where `VALUE` is set, substituted, or both. The **Result** column indicates the final value for `VALUE` in each scenario.
