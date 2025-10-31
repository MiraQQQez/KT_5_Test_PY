from api.base_request import BaseRequest
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class StoreAPI(BaseRequest):
    """
    Класс для работы с API магазина PetStore.
    Наследует BaseRequest и реализует методы для работы с заказами.
    """

    def __init__(self, base_url: str = 'https://petstore.swagger.io/v2'):
        """
        Инициализация StoreAPI.
        
        Args:
            base_url (str): Базовый URL API PetStore
        """
        super().__init__(base_url)
        self.endpoint = 'store'

    def get_inventory(self) -> Any:
        """
        Запрос 1: Получение инвентаря магазина.
        GET /store/inventory
        Возвращает количество питомцев по статусам.
        
        Returns:
            Any: Словарь с количеством питомцев по статусам
        """
        return self.get(f'{self.endpoint}/inventory')

    def place_order(self, order_data: Dict) -> Any:
        """
        Запрос 2: Создание заказа на питомца.
        POST /store/order
        
        Args:
            order_data (Dict): Данные заказа
                {
                    "id": 0,
                    "petId": 0,
                    "quantity": 0,
                    "shipDate": "2024-10-30T12:00:00.000Z",
                    "status": "placed",
                    "complete": true
                }
                
        Returns:
            Any: Данные созданного заказа
        """
        return self.post(f'{self.endpoint}/order', json_data=order_data)

    def get_order_by_id(self, order_id: int) -> Any:
        """
        Запрос 3: Получение заказа по ID.
        GET /store/order/{orderId}
        
        Args:
            order_id (int): ID заказа
            
        Returns:
            Any: Данные заказа
        """
        return self.get(f'{self.endpoint}/order', endpoint_id=str(order_id))

    def delete_order(self, order_id: int) -> Any:
        """
        Запрос 4: Удаление заказа.
        DELETE /store/order/{orderId}
        
        Args:
            order_id (int): ID заказа для удаления
            
        Returns:
            Any: Ответ от сервера
        """
        return self.delete(f'{self.endpoint}/order', endpoint_id=str(order_id))


# ========== Pydantic модели для валидации данных Store ==========

class Order(BaseModel):
    """
    Модель заказа для валидации данных.
    Используется для проверки ответов от API.
    """
    id: Optional[int] = Field(default=None, description="ID заказа")
    petId: int = Field(..., ge=0, description="ID питомца")
    quantity: int = Field(default=1, ge=0, description="Количество")
    shipDate: Optional[str] = Field(default=None, description="Дата доставки")
    status: str = Field(default="placed", description="Статус заказа")
    complete: bool = Field(default=False, description="Заказ завершен")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Валидация статуса заказа."""
        allowed_statuses = ['placed', 'approved', 'delivered']
        if v not in allowed_statuses:
            raise ValueError(f'Статус должен быть одним из: {allowed_statuses}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": 10,
                "petId": 198772,
                "quantity": 7,
                "shipDate": "2024-10-31T12:00:00.000Z",
                "status": "approved",
                "complete": True
            }
        }


class OrderCreate(BaseModel):
    """
    Модель для создания заказа.
    Автогенерация JSON для POST запросов.
    """
    id: Optional[int] = Field(default=None, description="ID заказа (опционально)")
    petId: int = Field(..., gt=0, description="ID питомца (обязательно)")
    quantity: int = Field(default=1, ge=1, le=1000, description="Количество (1-1000)")
    shipDate: Optional[str] = Field(default=None, description="Дата доставки")
    status: str = Field(default="placed", description="Статус заказа")
    complete: bool = Field(default=False, description="Заказ завершен")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Валидация статуса заказа."""
        allowed_statuses = ['placed', 'approved', 'delivered']
        if v not in allowed_statuses:
            raise ValueError(f'Статус должен быть одним из: {allowed_statuses}')
        return v

    def to_dict(self) -> Dict:
        """Конвертация модели в словарь для API запроса."""
        return self.model_dump(exclude_none=True)


class Inventory(BaseModel):
    """
    Модель для инвентаря магазина.
    Динамические поля для статусов питомцев.
    """
    class Config:
        extra = 'allow'  # Разрешаем дополнительные поля