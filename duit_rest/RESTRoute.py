from typing import Generic, TypeVar

T = TypeVar("T")


class RESTRoute(Generic[T]):
    """
    Represents a REST route that associates a name with a data model.
    """

    def __init__(self, name: str, model: T):
        """
        Initializes a RESTRoute instance.

        :param name: The name of the route.
        :param model: The data model to be linked with the route.
        """
        self.name = name
        self.model = model
