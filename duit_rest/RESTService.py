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
    def __init__(self, host: str = "0.0.0.0", port: int = 9420, **kwargs):
        self.host = host
        self.port = port

        self.app = FastAPI(**kwargs)

        self.settings_handler = DefaultSettings

    def add_route(self, name: str, model: T):
        self.add_route_endpoint(name, model)

        # create router
        router = APIRouter(prefix=name)

        # find endpoints
        finder: AnnotationFinder[RESTEndpoint] = AnnotationFinder(RESTEndpoint)

        for field_name, (data_field, annotation) in finder.find(model).items():
            if annotation.name is not None:
                field_name = annotation.name
            self.add_datafield_endpoint(field_name, data_field, annotation, router)

        self.app.include_router(router)

    def add_route_endpoint(self, name: str, model: T, router: Optional[APIRouter] = None):
        if router is None:
            router = self.app

        endpoint_path = f"{name}"

        def _handle_get(m: T):
            return self.settings_handler.serialize(m)

        def _handle_post(m: T, data: dict):
            self.settings_handler.deserialize(data, m)
            return self.settings_handler.serialize(m)

        router.add_api_route(endpoint_path, endpoint=partial(_handle_get, model), methods=["GET"])
        router.add_api_route(endpoint_path, endpoint=partial(_handle_post, model), methods=["POST"])

    def add_datafield_endpoint(self, name: str, field: DataField, annotation: RESTEndpoint,
                               router: Optional[APIRouter] = None):
        endpoint_path = f"/{name}"
        field_type = type(field.value)
        serializer = self.settings_handler._get_matching_serializer(field)

        if router is None:
            router = self.app

        def _serialize_data(f: DataField) -> Any:
            success, data = serializer.serialize(f.value)
            return data

        def _handle_get(f: DataField, value: Optional[str] = None) -> Any:
            if value is not None:
                unpacked_value = self._try_unpack(value)
                success, data = serializer.deserialize(field_type, unpacked_value)
                f.value = data

            return _serialize_data(f)

        router.add_api_route(endpoint_path, endpoint=partial(_handle_get, field), methods=["GET"])

    @staticmethod
    def _try_unpack(value: str) -> Any:
        try:
            return json.loads(value)
        except JSONDecodeError as ex:
            return value

    def run(self, blocking: bool = True) -> Optional[threading.Thread]:
        if blocking:
            uvicorn.run(self.app, host=self.host, port=self.port)
            return None

        def _run():
            uvicorn.run(self.app, host=self.host, port=self.port)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return thread
