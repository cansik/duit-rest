from typing import Optional, TypeVar

from duit.annotation.Annotation import Annotation
from duit.model.DataField import DataField

from duit_rest import REST_ROUTE_ANNOTATION_ATTRIBUTE_NAME

M = TypeVar("M", bound=DataField)


class RESTEndpoint(Annotation):
    """
    Represents a REST endpoint annotation that can be applied to a data model.

    This class allows associating a name with a specific REST endpoint
    and applies the annotation to a data model of type `DataField`.
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initializes the RESTEndpoint annotation.

        :param name: An optional string to specify the name of the REST endpoint.
        """
        self.name = name

    def _apply_annotation(self, model: M) -> M:
        """
        Applies the annotation to a data model instance.

        :param model: The data model instance to which the annotation is applied.
                      Must be an instance of `DataField`.

        :raises Exception: If the model is not an instance of `DataField`.

        :returns: The modified data model instance with the annotation applied.
        """
        if not isinstance(model, DataField):
            raise Exception(f"{type(self).__name__} can not be applied to {type(model).__name__}")

        # add attribute to data model
        model.__setattr__(self._get_annotation_attribute_name(), self)
        return model

    @staticmethod
    def _get_annotation_attribute_name() -> str:
        """
        Retrieves the name of the attribute used for storing the annotation.

        :returns: The name of the attribute as a string.
        """
        return REST_ROUTE_ANNOTATION_ATTRIBUTE_NAME
