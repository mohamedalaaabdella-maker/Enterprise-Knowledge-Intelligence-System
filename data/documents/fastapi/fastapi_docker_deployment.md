# FastAPI in Containers - Docker

Source: FastAPI Documentation
URL: https://fastapi.tiangolo.com/deployment/docker/
Version: 0.141.1
License: MIT (license of the original documentation; this file is an excerpt reformatted as Markdown)

## Build a Docker Image for FastAPI

Okay, let's build something now! 🚀

I'll show you how to build a **Docker image** for FastAPI **from scratch**, based on the **official Python** image.

This is what you would want to do in **most cases**, for example:

* Using **Kubernetes** or similar tools
* When running on a **Raspberry Pi**
* Using a cloud service that would run a container image for you, etc.

### Package Requirements

When you manage your project with `uv`, its direct dependencies are declared in `pyproject.toml` and the exact resolved versions are stored in `uv.lock`.

You can add the packages your application needs with:

```console
$ uv add "fastapi[standard]" pydantic
---> 100%
```

> **Note**
>
> The Dockerfile below uses `pip` inside the container. You can export the locked dependencies from your uv project to the `requirements.txt` format it expects:
>
>
> ```console
> $ uv export --format requirements-txt --no-dev --no-emit-project --output-file requirements.txt
> ```
>
>
> The generated `requirements.txt` is an export for the container build. Continue managing dependencies with `uv add` and regenerate it when `uv.lock` changes.
>

### Create the FastAPI Code

* Create an `app` directory and enter it.
* Create an empty file `__init__.py`.
* Create a `main.py` file with:

```Python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

### Dockerfile

Now in the same project directory create a file `Dockerfile` with:

```{ .dockerfile .annotate }
# (1)!
FROM python:3.14

# (2)!
WORKDIR /code

# (3)!
COPY ./requirements.txt /code/requirements.txt

# (4)!
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# (5)!
COPY ./app /code/app

# (6)!
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

1. Start from the official Python base image.

2. Set the current working directory to `/code`.

    This is where we'll put the `requirements.txt` file and the `app` directory.

3. Copy the file with the requirements to the `/code` directory.

    Copy **only** the file with the requirements first, not the rest of the code.

    As this file **doesn't change often**, Docker will detect it and use the **cache** for this step, enabling the cache for the next step too.

4. Install the package dependencies in the requirements file.

    The `--no-cache-dir` option tells `pip` to not save the downloaded packages locally, as that is only if `pip` was going to be run again to install the same packages, but that's not the case when working with containers.

> **Note**
>
>     The `--no-cache-dir` is only related to `pip`, it has nothing to do with Docker or containers.
>

    The `--upgrade` option tells `pip` to upgrade the packages if they are already installed.

    Because the previous step copying the file could be detected by the **Docker cache**, this step will also **use the Docker cache** when available.

    Using the cache in this step will **save** you a lot of **time** when building the image again and again during development, instead of **downloading and installing** all the dependencies **every time**.

5. Copy the `./app` directory inside the `/code` directory.

    As this has all the code which is what **changes most frequently** the Docker **cache** won't be used for this or any **following steps** easily.

    So, it's important to put this **near the end** of the `Dockerfile`, to optimize the container image build times.

6. Set the **command** to use `fastapi run`, which uses Uvicorn underneath.

    `CMD` takes a list of strings, each of these strings is what you would type in the command line separated by spaces.

    This command will be run from the **current working directory**, the same `/code` directory you set above with `WORKDIR /code`.

> **Tip**
>
> Review what each line does by clicking each number bubble in the code. 👆
>

> **Warning**
>
> Make sure to **always** use the **exec form** of the `CMD` instruction, as explained below.
>

#### Use CMD - Exec Form

The `CMD` Docker instruction can be written using two forms:

✅ **Exec** form:

```Dockerfile
# ✅ Do this
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

⛔️ **Shell** form:

```Dockerfile
# ⛔️ Don't do this
CMD fastapi run app/main.py --port 80
```

Make sure to always use the **exec** form to ensure that FastAPI can shutdown gracefully and lifespan events are triggered.

You can read more about it in the Docker docs for shell and exec form.

This can be quite noticeable when using `docker compose`. See this Docker Compose FAQ section for more technical details: Why do my services take 10 seconds to recreate or stop?.

#### Directory Structure

You should now have a directory structure like:

```
.
├── app
│   ├── __init__.py
│   └── main.py
├── Dockerfile
└── requirements.txt
```

#### Behind a TLS Termination Proxy

If you are running your container behind a TLS Termination Proxy (load balancer) like Nginx or Traefik, add the option `--proxy-headers`, this will tell Uvicorn (through the FastAPI CLI) to trust the headers sent by that proxy telling it that the application is running behind HTTPS, etc.

```Dockerfile
CMD ["fastapi", "run", "app/main.py", "--proxy-headers", "--port", "80"]
```

#### Docker Cache

There's an important trick in this `Dockerfile`, we first copy the **file with the dependencies alone**, not the rest of the code. Let me tell you why that is.

```Dockerfile
COPY ./requirements.txt /code/requirements.txt
```

Docker and other tools **build** these container images **incrementally**, adding **one layer on top of the other**, starting from the top of the `Dockerfile` and adding any files created by each of the instructions of the `Dockerfile`.

Docker and similar tools also use an **internal cache** when building the image, if a file hasn't changed since the last time building the container image, then it will **reuse the same layer** created the last time, instead of copying the file again and creating a new layer from scratch.

Just avoiding the copy of files doesn't necessarily improve things too much, but because it used the cache for that step, it can **use the cache for the next step**. For example, it could use the cache for the instruction that installs dependencies with:

```Dockerfile
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
```

The file with the package requirements **won't change frequently**. So, by copying only that file, Docker will be able to **use the cache** for that step.

And then, Docker will be able to **use the cache for the next step** that downloads and installs those dependencies. And here's where we **save a lot of time**. ✨ ...and avoid boredom waiting. 😪😆

Downloading and installing the package dependencies **could take minutes**, but using the **cache** would **take seconds** at most.

And as you would be building the container image again and again during development to check that your code changes are working, there's a lot of accumulated time this would save.

Then, near the end of the `Dockerfile`, we copy all the code. As this is what **changes most frequently**, we put it near the end, because almost always, anything after this step will not be able to use the cache.

```Dockerfile
COPY ./app /code/app
```

### Build the Docker Image

Now that all the files are in place, let's build the container image.

* Go to the project directory (in where your `Dockerfile` is, containing your `app` directory).
* Build your FastAPI image:

```console
$ docker build -t myimage .

---> 100%
```

> **Tip**
>
> Notice the `.` at the end, it's equivalent to `./`, it tells Docker the directory to use to build the container image.
>
> In this case, it's the same current directory (`.`).
>

### Start the Docker Container

* Run a container based on your image:

```console
$ docker run -d --name mycontainer -p 80:80 myimage
```

## Previous Steps Before Starting and Containers

If you are using containers (e.g. Docker, Kubernetes), then there are two main approaches you can use.

### Multiple Containers

If you have **multiple containers**, probably each one running a **single process** (for example, in a **Kubernetes** cluster), then you would probably want to have a **separate container** doing the work of the **previous steps** in a single container, running a single process, **before** running the replicated worker containers.

> **Note**
>
> If you are using Kubernetes, this would probably be an Init Container.
>

If in your use case there's no problem in running those previous steps **multiple times in parallel** (for example if you are not running database migrations, but just checking if the database is ready yet), then you could also just put them in each container right before starting the main process.

### Single Container

If you have a simple setup, with a **single container** that then starts multiple **worker processes** (or also just one process), then you could run those previous steps in the same container, right before starting the process with the app.

### Base Docker Image

There used to be an official FastAPI Docker image: tiangolo/uvicorn-gunicorn-fastapi. But it is now deprecated. ⛔️

You should probably **not** use this base Docker image (or any other similar one).

If you are using **Kubernetes** (or others) and you are already setting **replication** at the cluster level, with multiple **containers**. In those cases, you are better off **building an image from scratch** as described above: Build a Docker Image for FastAPI.

And if you need to have multiple workers, you can simply use the `--workers` command line option.

> **Note: Technical Details**
>
> The Docker image was created when Uvicorn didn't support managing and restarting dead workers, so it was needed to use Gunicorn with Uvicorn, which added quite some complexity, just to have Gunicorn manage and restart the Uvicorn worker processes.
>
> But now that Uvicorn (and the `fastapi` command) support using `--workers`, there's no reason to use a base Docker image instead of building your own (it's pretty much the same amount of code 😅).
>
