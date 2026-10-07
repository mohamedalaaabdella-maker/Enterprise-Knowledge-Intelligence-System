# Docker Containers and Container Lifecycle

Source: Docker Documentation
URL: https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
License: Apache-2.0 (license of the original documentation; this file is an excerpt reformatted as Markdown)

## What Is a Container?

Imagine you're developing a killer web app that has three main components - a React frontend, a Python API, and a PostgreSQL database. If you wanted to work on this project, you'd have to install Node, Python, and PostgreSQL.

How do you make sure you have the same versions as the other developers on your team? Or your CI/CD system? Or what's used in production?

How do you ensure the version of Python (or Node or the database) your app needs isn't affected by what's already on your machine? How do you manage potential conflicts?

Enter containers!

What is a container? Simply put, containers are isolated processes for each of your app's components. Each component - the frontend React app, the Python API engine, and the database - runs in its own isolated environment, completely isolated from everything else on your machine.

Here's what makes them awesome. Containers are:

- Self-contained. Each container has everything it needs to function with no reliance on any pre-installed dependencies on the host machine.
- Isolated. Since containers run in isolation, they have minimal influence on the host and other containers, increasing the security of your applications.
- Independent. Each container is independently managed. Deleting one container won't affect any others.
- Portable. Containers can run anywhere! The container that runs on your development machine will work the same way in a data center or anywhere in the cloud!

### Containers versus virtual machines (VMs)

Without getting too deep, a VM is an entire operating system with its own kernel, hardware drivers, programs, and applications. Spinning up a VM only to isolate a single application is a lot of overhead.

A container is simply an isolated process with all of the files it needs to run. If you run multiple containers, they all share the same kernel, allowing you to run more applications on less infrastructure.

> **Using VMs and containers together**
>
> Quite often, you will see containers and VMs used together. As an example, in a cloud environment, the provisioned machines are typically VMs. However, instead of provisioning one machine to run one application, a VM with a container runtime can run multiple containerized applications, increasing resource utilization and reducing costs.

## Running, Listing and Stopping Containers with the CLI

**Using the CLI:**

Follow the instructions to run a container using the CLI:

1. Open your CLI terminal and start a container by using the `docker run` command:

    ```console
    $ docker run -d -p 8080:80 docker/welcome-to-docker
    ```

    The output from this command is the full container ID.

Congratulations! You just fired up your first container! 🎉

### View your running containers

You can verify if the container is up and running by using the `docker ps` command:

```console
docker ps
```

You will see output like the following:

```console
 CONTAINER ID   IMAGE                      COMMAND                  CREATED          STATUS          PORTS                      NAMES
 a1f7a4bb3a27   docker/welcome-to-docker   "/docker-entrypoint.…"   11 seconds ago   Up 11 seconds   0.0.0.0:8080->80/tcp       gracious_keldysh
```

This container runs a web server that displays a simple website. When working with more complex projects, you'll run different parts in different containers. For example, a different container for the `frontend`, `backend`, and `database`.

> **Tip**
>
> The `docker ps` command will show you _only_ running containers. To view stopped containers, add the `-a` flag to list all containers: `docker ps -a`

### Access the frontend

When you launched the container, you exposed one of the container's ports onto your machine. Think of this as creating configuration to let you to connect through the isolated environment of the container.

For this container, the frontend is accessible on port `8080`. To open the website, select the link in the **Port(s)** column of your container or visit http://localhost:8080 in your browser.

### Stop your container

The `docker/welcome-to-docker` container continues to run until you stop it. You can stop a container using the `docker stop` command.

1. Run `docker ps` to get the ID of the container

2. Provide the container ID or name to the `docker stop` command:

    ```console
    docker stop <the-container-id>
    ```

> **Tip**
>
> When referencing containers by ID, you don't need to provide the full ID. You only need to provide enough of the ID to make it unique. As an example, the previous container could be stopped by running the following command:
>
> ```console
> docker stop a1f
> ```

## Containers Are Ephemeral

When a container starts, it uses the files and configuration provided by the image. Each container is able to create, modify, and delete files and does so without affecting any other containers. When the container is deleted, these file changes are also deleted.

While this ephemeral nature of containers is great, it poses a challenge when you want to persist the data. For example, if you restart a database container, you might not want to start with an empty database. So, how do you persist files?

## Starting Containers Automatically: Restart Policies

To configure the restart policy for a container, use the `--restart` flag
when using the `docker run` command. The value of the `--restart` flag can be
any of the following:

| Flag                       | Description                                                                                                                                                                                                                                                                                                                                                           |
| :------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `no`                       | Don't automatically restart the container. (Default)                                                                                                                                                                                                                                                                                                                  |
| `on-failure[:max-retries]` | Restart the container if it exits due to an error, which manifests as a non-zero exit code. Optionally, limit the number of times the Docker daemon attempts to restart the container using the `:max-retries` option. The `on-failure` policy only prompts a restart if the container exits with a failure. It doesn't restart the container if the daemon restarts. |
| `always`                   | Always restart the container if it stops. If it's manually stopped, it's restarted only when Docker daemon restarts or the container itself is manually restarted. (See the second bullet listed in restart policy details)                                                                                                                |
| `unless-stopped`           | Similar to `always`, except that when the container is stopped (manually or otherwise), it isn't restarted even after Docker daemon restarts.                                                                                                                                                                                                                         |

The following command starts a Redis container with the `unless-stopped`
restart policy. Docker restarts the container if it exits or if the daemon
restarts, but not if you stopped the container yourself.

```console
$ docker run -d --name redis --restart unless-stopped redis
```

The following command changes the restart policy for an already running
container named `redis`.

```console
$ docker update --restart unless-stopped redis
```

The following command ensures all running containers restart.

```console
$ docker update --restart unless-stopped $(docker ps -q)
```

### Restart policy details

Keep the following in mind when using restart policies:

- A restart policy only takes effect after a container starts successfully. In
  this case, starting successfully means that the container is up for at least
  10 seconds and Docker has started monitoring it. This prevents a container
  which doesn't start at all from going into a restart loop.

- If you manually stop a container, the restart policy is ignored until the
  Docker daemon restarts or the container is manually restarted. This prevents
  a restart loop.

- Restart policies only apply to containers. To configure restart policies for
  Swarm services, see
  flags related to service restart.

### Restarting foreground containers

When you run a container in the foreground, stopping a container causes the
attached CLI to exit as well, regardless of the restart policy of the
container. This behavior is illustrated in the following example.

1. Create a Dockerfile that prints the numbers 1 to 5 and then exits.

   ```dockerfile
   FROM busybox:latest
   COPY --chmod=755 <<"EOF" /start.sh
   echo "Starting..."
   for i in $(seq 1 5); do
     echo "$i"
     sleep 1
   done
   echo "Exiting..."
   exit 1
   EOF
   ENTRYPOINT /start.sh
   ```

2. Build an image from the Dockerfile.

   ```console
   $ docker build -t startstop .
   ```

3. Run a container from the image, specifying `always` for its restart policy.

   The container prints the numbers 1..5 to stdout, and then exits. This causes
   the attached CLI to exit as well.

   ```console
   $ docker run --restart always startstop
   Starting...
   1
   2
   3
   4
   5
   Exiting...
   $
   ```

4. Running `docker ps` shows that is still running or restarting, thanks to the
   restart policy. The CLI session has already exited, however. It doesn't
   survive the initial container exit.

If restart policies don't suit your needs, such as when processes outside
Docker depend on Docker containers, you can use a process manager such as
systemd or
supervisor instead.

> **Warning**
>
> Don't combine Docker restart policies with host-level process managers,
> as this creates conflicts.

To use a process manager, configure it to start your container or service using
the same `docker start` or `docker service` command you would normally use to
start the container manually. Consult the documentation for the specific
process manager for more details.
