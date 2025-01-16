import json
import threading
from functools import partial
from json import JSONDecodeError
from typing import Generic, TypeVar, Optional, Any

import uvicorn
from duit.annotation.AnnotationFinder import AnnotationFinder
from duit.model.DataField import DataField
from duit.settings.Settings import DefaultSettings
from fastapi import FastAPI, APIRouter

from duit_rest.RESTEndpoint import RESTEndpoint

T = TypeVar('T')


class RESTService(Generic[T]):
    """
    A generic REST service for dynamically adding routes and handling API endpoints.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 9420, **kwargs):
        """
        Initializes the REST service.

        :param host: The host address to bind the service to.
        :param port: The port to bind the service to.
        :param kwargs: Additional FastAPI configuration options.
        """
        self.host = host
        self.port = port

        self.app = FastAPI(**kwargs)

        self.settings_handler = DefaultSettings

    def add_route(self, name: str, model: T):
        """
        Adds a route to the REST service.

        :param name: The base name of the route.
        :param model: The data model to associate with the route.
        """
        self.add_route_endpoint(name, model)

        # Create a router with the specified prefix
        router = APIRouter(prefix=name)

        # Find endpoints annotated in the model
        finder: AnnotationFinder[RESTEndpoint] = AnnotationFinder(RESTEndpoint)

        for field_name, (data_field, annotation) in finder.find(model).items():
            if annotation.name is not None:
                field_name = annotation.name
            self.add_datafield_endpoint(field_name, data_field, annotation, router)

        self.app.include_router(router)

    def add_route_endpoint(self, name: str, model: T, router: Optional[APIRouter] = None):
        """
        Adds a generic GET and POST route for a model.

        :param name: The route path name.
        :param model: The data model to be associated with the route.
        :param router: An optional router to add the route to. If None, the main FastAPI app is used.
        """
        if router is None:
            router = self.app

        endpoint_path = f"{name}"

        def _handle_get(m: T):
            """
            Handles a GET request for the model.

            :param m: The model instance to serialize.
            :returns: The serialized model.
            """
            return self.settings_handler.serialize(m)

        def _handle_post(m: T, data: dict):
            """
            Handles a POST request for the model.

            :param m: The model instance to update.
            :param data: The dictionary to deserialize into the model.
            :returns: The updated serialized model.
            """
            self.settings_handler.deserialize(data, m)
            return self.settings_handler.serialize(m)

        router.add_api_route(endpoint_path, endpoint=partial(_handle_get, model), methods=["GET"])
        router.add_api_route(endpoint_path, endpoint=partial(_handle_post, model), methods=["POST"])

    def add_datafield_endpoint(self, name: str, field: DataField, annotation: RESTEndpoint,
                               router: Optional[APIRouter] = None):
        """
        Adds an endpoint for a specific data field.

        :param name: The name of the data field.
        :param field: The `DataField` instance to handle.
        :param annotation: The REST endpoint annotation for the field.
        :param router: An optional router to add the endpoint to. If None, the main FastAPI app is used.
        """
        endpoint_path = f"/{name}"
        field_type = type(field.value)
        serializer = self.settings_handler._get_matching_serializer(field)

        if router is None:
            router = self.app

        def _serialize_data(f: DataField) -> Any:
            """
            Serializes the data field's value.

            :param f: The data field to serialize.
            :returns: The serialized value.
            """
            success, data = serializer.serialize(f.value)
            return data

        def _handle_get(f: DataField, value: Optional[str] = None) -> Any:
            """
            Handles a GET request for the data field.

            :param f: The data field instance to retrieve or update.
            :param value: An optional value to update the field with.
            :returns: The serialized value of the field.
            """
            if value is not None:
                unpacked_value = self._try_unpack(value)
                success, data = serializer.deserialize(field_type, unpacked_value)
                f.value = data

            return _serialize_data(f)

        router.add_api_route(endpoint_path, endpoint=partial(_handle_get, field), methods=["GET"])

    @staticmethod
    def _try_unpack(value: str) -> Any:
        """
        Attempts to unpack a string value as JSON.

        :param value: The string to unpack.
        :returns: The unpacked JSON value or the original string if JSON decoding fails.
        """
        try:
            return json.loads(value)
        except JSONDecodeError:
            return value

    def run(self, blocking: bool = True) -> Optional[threading.Thread]:
        """
        Runs the REST service.

        :param blocking: If True, the server will run in the current thread.
                         If False, the server will run in a separate thread.
        :returns: A threading.Thread instance if `blocking` is False, otherwise None.
        """
        if blocking:
            uvicorn.run(self.app, host=self.host, port=self.port)
            return None

        def _run():
            uvicorn.run(self.app, host=self.host, port=self.port)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return thread
