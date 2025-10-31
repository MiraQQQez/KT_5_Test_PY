from api.base_request import BaseRequest
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

class UserAPI(BaseRequest):
    """
    Класс для работы с API пользователей PetStore.
    Наследует BaseRequest и реализует методы для работы с пользователями.
    """

    def __init__(self, base_url: str = 'https://petstore.swagger.io/v2'):
        """
        Инициализация UserAPI.
        
        Args:
            base_url (str): Базовый URL API PetStore
        """
        super().__init__(base_url)
        self.endpoint = 'user'

    def create_user(self, user_data: Dict) -> Any:
        """
        Запрос 1: Создание нового пользователя.
        POST /user
        
        Args:
            user_data (Dict): Данные пользователя
                {
                    "id": 0,
                    "username": "string",
                    "firstName": "string",
                    "lastName": "string",
                    "email": "string",
                    "password": "string",
                    "phone": "string",
                    "userStatus": 0
                }
                
        Returns:
            Any: Ответ от сервера
        """
        return self.post(self.endpoint, json_data=user_data)

    def get_user_by_username(self, username: str) -> Any:
        """
        Запрос 2: Получение пользователя по имени.
        GET /user/{username}
        
        Args:
            username (str): Имя пользователя
            
        Returns:
            Any: Данные пользователя
        """
        return self.get(self.endpoint, endpoint_id=username)

    def update_user(self, username: str, user_data: Dict) -> Any:
        """
        Запрос 3: Обновление данных пользователя.
        PUT /user/{username}
        
        Args:
            username (str): Имя пользователя
            user_data (Dict): Обновленные данные пользователя
            
        Returns:
            Any: Ответ от сервера
        """
        return self.put(self.endpoint, json_data=user_data, endpoint_id=username)

    def delete_user(self, username: str) -> Any:
        """
        Запрос 4: Удаление пользователя.
        DELETE /user/{username}
        
        Args:
            username (str): Имя пользователя для удаления
            
        Returns:
            Any: Ответ от сервера
        """
        return self.delete(self.endpoint, endpoint_id=username)


# ========== Pydantic модели для валидации данных User ==========

class User(BaseModel):
    """
    Модель пользователя для валидации данных.
    Используется для проверки ответов от API.
    """
    id: Optional[int] = Field(default=None, description="ID пользователя")
    username: str = Field(..., min_length=1, max_length=50, description="Имя пользователя")
    firstName: Optional[str] = Field(default=None, max_length=50, description="Имя")
    lastName: Optional[str] = Field(default=None, max_length=50, description="Фамилия")
    email: Optional[str] = Field(default=None, description="Email")
    password: Optional[str] = Field(default=None, min_length=6, description="Пароль")
    phone: Optional[str] = Field(default=None, description="Телефон")
    userStatus: Optional[int] = Field(default=0, description="Статус пользователя")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "username": "testuser",
                "firstName": "Test",
                "lastName": "User",
                "email": "test@example.com",
                "password": "password123",
                "phone": "+1234567890",
                "userStatus": 1
            }
        }


class UserCreate(BaseModel):
    """
    Модель для создания пользователя.
    Автогенерация JSON для POST запросов.
    """
    id: Optional[int] = Field(default=None, description="ID пользователя (опционально)")
    username: str = Field(..., min_length=1, max_length=50, description="Имя пользователя (обязательно)")
    firstName: str = Field(..., max_length=50, description="Имя (обязательно)")
    lastName: str = Field(..., max_length=50, description="Фамилия (обязательно)")
    email: str = Field(..., description="Email (обязательно)")
    password: str = Field(..., min_length=6, description="Пароль (обязательно, минимум 6 символов)")
    phone: Optional[str] = Field(default=None, description="Телефон")
    userStatus: int = Field(default=0, ge=0, le=10, description="Статус пользователя (0-10)")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Валидация email адреса."""
        if '@' not in v or '.' not in v:
            raise ValueError('Некорректный email адрес')
        return v

    def to_dict(self) -> Dict:
        """Конвертация модели в словарь для API запроса."""
        return self.model_dump(exclude_none=True)


class UserUpdate(BaseModel):
    """
    Модель для обновления пользователя.
    Все поля опциональны.
    """
    id: Optional[int] = Field(default=None, description="ID пользователя")
    username: Optional[str] = Field(default=None, min_length=1, max_length=50, description="Имя пользователя")
    firstName: Optional[str] = Field(default=None, max_length=50, description="Имя")
    lastName: Optional[str] = Field(default=None, max_length=50, description="Фамилия")
    email: Optional[str] = Field(default=None, description="Email")
    password: Optional[str] = Field(default=None, min_length=6, description="Пароль")
    phone: Optional[str] = Field(default=None, description="Телефон")
    userStatus: Optional[int] = Field(default=None, ge=0, le=10, description="Статус пользователя")

    def to_dict(self) -> Dict:
        """Конвертация модели в словарь для API запроса."""
        return self.model_dump(exclude_none=True)