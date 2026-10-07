# FastAPI Security: OAuth2 Password Flow and JWT

Source: FastAPI Documentation
URL: https://fastapi.tiangolo.com/tutorial/security/first-steps/
Version: 0.141.1
License: MIT (license of the original documentation; this file is an excerpt reformatted as Markdown)

## The password flow

Now let's go back a bit and understand what all that is.

The `password` "flow" is one of the ways ("flows") defined in OAuth2, to handle security and authentication.

OAuth2 was designed so that the backend or API could be independent of the server that authenticates the user.

But in this case, the same **FastAPI** application will handle the API and the authentication.

So, let's review it from that simplified point of view:

* The user types the `username` and `password` in the frontend, and hits `Enter`.
* The frontend (running in the user's browser) sends that `username` and `password` to a specific URL in our API (declared with `tokenUrl="token"`).
* The API checks that `username` and `password`, and responds with a "token" (we haven't implemented any of this yet).
    * A "token" is just a string with some content that we can use later to verify this user.
    * Normally, a token is set to expire after some time.
        * So, the user will have to log in again at some point later.
        * And if the token is stolen, the risk is less. It is not like a permanent key that will work forever (in most of the cases).
* The frontend stores that token temporarily somewhere.
* The user clicks in the frontend to go to another section of the frontend web app.
* The frontend needs to fetch some more data from the API.
    * But it needs authentication for that specific endpoint.
    * So, to authenticate with our API, it sends a header `Authorization` with a value of `Bearer ` plus the token.
    * If the token contains `foobar`, the content of the `Authorization` header would be: `Bearer foobar`.

## FastAPI's OAuth2PasswordBearer

**FastAPI** provides several tools, at different levels of abstraction, to implement these security features.

In this example we are going to use **OAuth2**, with the **Password** flow, using a **Bearer** token. We do that using the `OAuth2PasswordBearer` class.

> **Note**
>
> A "bearer" token is not the only option.
>
> But it's the best one for our use case.
>
> And it might be the best for most use cases, unless you are an OAuth2 expert and know exactly why there's another option that better suits your needs.
>
> In that case, **FastAPI** also provides you with the tools to build it.
>

When we create an instance of the `OAuth2PasswordBearer` class we pass in the `tokenUrl` parameter. This parameter contains the URL that the client (the frontend running in the user's browser) will use to send the `username` and `password` in order to get a token.

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
```

> **Tip**
>
> Here `tokenUrl="token"` refers to a relative URL `token` that we haven't created yet. As it's a relative URL, it's equivalent to `./token`.
>
> Because we are using a relative URL, if your API was located at `https://example.com/`, then it would refer to `https://example.com/token`. But if your API was located at `https://example.com/api/v1/`, then it would refer to `https://example.com/api/v1/token`.
>
> Using a relative URL is important to make sure your application keeps working even in an advanced use case like Behind a Proxy.
>

This parameter doesn't create that endpoint / *path operation*, but declares that the URL `/token` will be the one that the client should use to get the token. That information is used in OpenAPI, and then in the interactive API documentation systems.

We will soon also create the actual path operation.

> **Note**
>
> If you are a very strict "Pythonista" you might dislike the style of the parameter name `tokenUrl` instead of `token_url`.
>
> That's because it is using the same name as in the OpenAPI spec. So that if you need to investigate more about any of these security schemes you can just copy and paste it to find more information about it.
>

The `oauth2_scheme` variable is an instance of `OAuth2PasswordBearer`, but it is also a "callable".

It could be called as:

```Python
oauth2_scheme(some, parameters)
```

So, it can be used with `Depends`.

### Use it

Now you can pass that `oauth2_scheme` in a dependency with `Depends`.

## What it does

It will go and look in the request for that `Authorization` header, check if the value is `Bearer ` plus some token, and will return the token as a `str`.

If it doesn't see an `Authorization` header, or the value doesn't have a `Bearer ` token, it will respond with a 401 status code error (`UNAUTHORIZED`) directly.

You don't even have to check if the token exists to return an error. You can be sure that if your function is executed, it will have a `str` in that token.

You can try it already in the interactive docs:

We are not verifying the validity of the token yet, but that's a start already.

## About JWT

JWT means "JSON Web Tokens".

It's a standard to codify a JSON object in a long dense string without spaces. It looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

It is not encrypted, so, anyone could recover the information from the contents.

But it's signed. So, when you receive a token that you issued, you can verify that it was you who issued it.

That way, you can create a token with an expiration of, let's say, 1 week. And then when the user comes back the next day with the token, you know that user is still logged in to your system.

After a week, the token will be expired and the user will not be authorized and will have to sign in again to get a new token. And if the user (or a third party) tried to modify the token to change the expiration, you would be able to discover it, because the signatures would not match.

If you want to play with JWT tokens and see how they work, check https://jwt.io.

## Password hashing

"Hashing" means converting some content (a password in this case) into a sequence of bytes (just a string) that looks like gibberish.

Whenever you pass exactly the same content (exactly the same password) you get exactly the same gibberish.

But you cannot convert from the gibberish back to the password.

### Why use password hashing

If your database is stolen, the thief won't have your users' plaintext passwords, only the hashes.

So, the thief won't be able to try to use that password in another system (as many users use the same password everywhere, this would be dangerous).

## Handle JWT tokens

Import the modules installed.

Create a random secret key that will be used to sign the JWT tokens.

To generate a secure random secret key use the command:

```console
$ openssl rand -hex 32

09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
```

And copy the output to the variable `SECRET_KEY` (don't use the one in the example).

Create a variable `ALGORITHM` with the algorithm used to sign the JWT token and set it to `"HS256"`.

Create a variable for the expiration of the token.

Define a Pydantic Model that will be used in the token endpoint for the response.

Create a utility function to generate a new access token.
