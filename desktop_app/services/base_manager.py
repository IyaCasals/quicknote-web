from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class BaseManager(ABC):
    def __init__(self, session: Session):
        self._session = session

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, *args, **kwargs):
        raise NotImplementedError
