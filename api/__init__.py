"""Модуль API для работы с PetStore."""

from .base_request import BaseRequest
from .user_api import UserAPI
from .store_api import StoreAPI

__all__ = ['BaseRequest', 'UserAPI', 'StoreAPI']
