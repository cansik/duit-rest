from typing import Generic, TypeVar

T = TypeVar('T')


class RESTRoute(Generic[T]):
    def __init__(self, name: str, model: T):
        self.name = name
        self.model = model
