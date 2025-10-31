"""Тесты для Store API с использованием Allure и Pydantic."""

import pytest
import allure
from api.store_api import StoreAPI, Order, OrderCreate, Inventory
from datetime import datetime


@allure.feature('Store API')
@allure.story('Inventory')
class TestStoreInventory:
    """Тесты для работы с инвентарем магазина."""

    @allure.title('Получение инвентаря магазина')
    @allure.description('Проверка получения инвентаря магазина с количеством питомцев по статусам')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_inventory(self, store_api):
        """Тест получения инвентаря магазина."""
        with allure.step('Отправка GET запроса на /store/inventory'):
            response = store_api.get_inventory()
        
        with allure.step('Проверка что ответ является словарем'):
            assert isinstance(response, dict), "Ответ должен быть словарем"
        
        with allure.step('Проверка что в ответе есть данные'):
            assert len(response) > 0, "Инвентарь не должен быть пустым"
        
        allure.attach(
            str(response),
            name="Inventory Response",
            attachment_type=allure.attachment_type.JSON
        )


@allure.feature('Store API')
@allure.story('Orders')
class TestStoreOrders:
    """Тесты для работы с заказами."""

    @allure.title('Создание нового заказа')
    @allure.description('Проверка создания заказа с валидацией через Pydantic')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_order(self, store_api):
        """Тест создания заказа."""
        with allure.step('Создание данных заказа через Pydantic'):
            order_data = OrderCreate(
                id=12345,
                petId=100,
                quantity=5,
                shipDate=datetime.now().isoformat() + 'Z',
                status='placed',
                complete=False
            )
            allure.attach(
                str(order_data.to_dict()),
                name="Order Data",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step('Отправка POST запроса на /store/order'):
            response = store_api.place_order(order_data.to_dict())
        
        with allure.step('Валидация ответа через Pydantic модель Order'):
            order = Order(**response)
            assert order.id is not None, "ID заказа должен быть установлен"
            assert order.petId == 100, "ID питомца должен совпадать"
            assert order.quantity == 5, "Количество должно совпадать"
        
        allure.attach(
            str(response),
            name="Create Order Response",
            attachment_type=allure.attachment_type.JSON
        )
        
        return order.id

    @allure.title('Получение заказа по ID')
    @allure.description('Проверка получения существующего заказа')
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_order_by_id(self, store_api, create_test_order):
        """Тест получения заказа по ID."""
        order_id = create_test_order
        
        with allure.step(f'Отправка GET запроса на /store/order/{order_id}'):
            response = store_api.get_order_by_id(order_id)
        
        with allure.step('Валидация ответа через Pydantic'):
            order = Order(**response)
            assert order.id == order_id, "ID заказа должен совпадать"
        
        allure.attach(
            str(response),
            name="Get Order Response",
            attachment_type=allure.attachment_type.JSON
        )

    @allure.title('Удаление заказа')
    @allure.description('Проверка удаления существующего заказа')
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_order(self, store_api, create_test_order):
        """Тест удаления заказа."""
        order_id = create_test_order
        
        with allure.step(f'Отправка DELETE запроса на /store/order/{order_id}'):
            response = store_api.delete_order(order_id)
        
        with allure.step('Проверка успешного удаления'):
            assert response is not None, "Ответ не должен быть пустым"
        
        allure.attach(
            str(response),
            name="Delete Order Response",
            attachment_type=allure.attachment_type.TEXT
        )
