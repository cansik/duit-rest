from typing import Optional, TypeVar

from duit.annotation.Annotation import Annotation
from duit.model.DataField import DataField

from duit_rest import REST_ROUTE_ANNOTATION_ATTRIBUTE_NAME

M = TypeVar("M", bound=DataField)


class RESTEndpoint(Annotation):

    def __init__(self, name: Optional[str] = None):
        self.name = name

    def _apply_annotation(self, model: M) -> M:
        if not isinstance(model, DataField):
            raise Exception(f"{type(self).__name__} can not be applied to {type(model).__name__}")

        # add attribute to data model
        model.__setattr__(self._get_annotation_attribute_name(), self)
        return model

    @staticmethod
    def _get_annotation_attribute_name() -> str:
        return REST_ROUTE_ANNOTATION_ATTRIBUTE_NAME
