# REST for Duit

[![PyPI](https://img.shields.io/pypi/v/duit-rest)](https://pypi.org/project/duit-rest/)
[![Github](https://img.shields.io/badge/duit-rest?logo=github&label=github&color=green)](https://github.com/cansik/duit-rest)

A web-based REST API for duit datafields.

This is an addon module for the data ui toolkit ([duit](https://github.com/cansik/duit)) which adds REST API support
for [DataFields](https://cansik.github.io/duit/duit.html#data-field).

## Installation

The package can be installed directly from [PyPI](https://pypi.org/project/duit-rest/).

```

pip install duit-rest

```

## Documentation

Duit-rest uses [FastAPI](https://fastapi.tiangolo.com/) as REST backend to handle HTTP requests. The main class is the
`RESTService` which handles the HTTP server and maps the annotated `DataFields` to the corresponding endpoints.

### RESTEndpoint

It is possible to annotate existing `DataFields` with the `RESTEndpoint` annotation. This annotation later tells the
`RESTService` if the field has to be exposed over REST. It is recommended to gather all DataFields in a single object:

```python
from duit_rest.RESTEndpoint import RESTEndpoint


class Config:
    def __init__(self):
        self.name = DataField("Cat") | RESTEndpoint()
```

By default, the name of the variable (e.g. `name`) is used as REST endpoint identifier. It is possible to change the
name through the `RESTEndpoint` annotation.

```python
self.name = DataField("Cat") | RESTEndpoint(name="the-cats-name")
```

### RESTService

The RESTService handles the HTTP server and mapping with the `DataFields`. Here is a simple example on how to create a
`RESTService`, add the previously defined config and start the service.

```python
# create an actual instance of the config
config = Config()

# create a rest service
rest_service = RESTService()

# add the config object (create mapping) under the route "/config"
rest_service.add_route("/config", config)

# run the service
rest_service.run()
```

#### Settings

The `RESTService` has several default arguments that can be changed before the service is started:

```python
# RESTService parameters and their default values
host: str = "0.0.0.0",  # on which interface the service is running
port: int = 9420,  # on which port the service is running
title: str = "REST API"  # title of the API
```

#### Routes

It is possible to add various objects to the RESTService, each with a unique route (address).

```python
rest_service.add_route("/config", config)
```

Each `DataField` is accessible under this route, so for example the `name` field would be available at `/config/name`.

#### API Usage

Getting values:

```bash
# Get entire configuration
GET http://localhost:9420/config

# Get specific field
GET http://localhost:9420/config/name
```

Setting values:

```bash
# Update entire configuration
POST http://localhost:9420/config
Content-Type: application/json

{
    "name": "NewName",
    "age": 25
}

# Update specific field
GET http://localhost:9420/config/name?value="NewName"
```

#### Start

To start the service, call the `run()` method. This is a blocking method that doesn't return until the service is
shutdown:

```python
# run blocking
rest_service.run()
```

To start the service in its own thread, set the `blocking` argument to `False:

```python
# run non-blocking
thread = rest_service.run(blocking=False)
```

## About

Copyright (c) 2025 Florian Bruggisser
