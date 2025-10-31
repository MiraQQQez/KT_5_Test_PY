"""
Фикстуры для тестов PetStore API.
Используются во всех тестовых модулях.
"""

import pytest
import allure
from api.user_api import UserAPI, UserCreate
from api.store_api import StoreAPI, OrderCreate
from datetime import datetime
import random
import string


def generate_random_username(length=10):
    """Генерация случайного имени пользователя."""
    return 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


# ========== Фикстуры для API клиентов ==========

@pytest.fixture(scope="session")
def base_url():
    """Базовый URL для PetStore API."""
    return "https://petstore.swagger.io/v2"


@pytest.fixture(scope="class")
def user_api(base_url):
    """Фикстура для User API клиента."""
    with allure.step('Инициализация User API клиента'):
        api = UserAPI(base_url)
    return api


@pytest.fixture(scope="class")
def store_api(base_url):
    """Фикстура для Store API клиента."""
    with allure.step('Инициализация Store API клиента'):
        api = StoreAPI(base_url)
    return api


# ========== Фикстуры для создания тестовых данных ==========

@pytest.fixture(scope="function")
def create_test_user(user_api):
    """
    Фикстура для создания тестового пользователя.
    Создает пользователя перед тестом и возвращает его username.
    """
    username = generate_random_username()
    
    with allure.step(f'Создание тестового пользователя: {username}'):
        user_data = UserCreate(
            id=random.randint(10000, 99999),
            username=username,
            firstName="Test",
            lastName="User",
            email="test@example.com",
            password="password123",
            phone="+1234567890",
            userStatus=1
        )
        user_api.create_user(user_data.to_dict())
    
    yield username
    
    # Cleanup: удаляем пользователя после теста
    with allure.step(f'Удаление тестового пользователя: {username}'):
        try:
            user_api.delete_user(username)
        except Exception as e:
            print(f"Не удалось удалить пользователя {username}: {e}")


@pytest.fixture(scope="function")
def create_test_order(store_api):
    """
    Фикстура для создания тестового заказа.
    Создает заказ перед тестом и возвращает его ID.
    """
    with allure.step('Создание тестового заказа'):
        order_data = OrderCreate(
            id=random.randint(1, 10),
            petId=random.randint(1, 100),
            quantity=random.randint(1, 10),
            shipDate=datetime.now().isoformat() + 'Z',
            status='placed',
            complete=False
        )
        response = store_api.place_order(order_data.to_dict())
        order_id = response.get('id')
    
    yield order_id
    
    # Cleanup: удаляем заказ после теста
    with allure.step(f'Удаление тестового заказа: {order_id}'):
        try:
            store_api.delete_order(order_id)
        except Exception as e:
            print(f"Не удалось удалить заказ {order_id}: {e}")


# ========== Хуки для Allure отчетов ==========

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук для добавления дополнительной информации в Allure отчет.
    Добавляет скриншоты и логи при падении тестов.
    """
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == 'call' and rep.failed:
        # Добавляем информацию об ошибке в Allure
        if hasattr(item, 'funcargs'):
            allure.attach(
                str(item.funcargs),
                name="Test Arguments",
                attachment_type=allure.attachment_type.TEXT
            )


def pytest_configure(config):
    """Конфигурация pytest перед запуском тестов."""
    # Добавляем кастомные маркеры
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "critical: mark test as critical"
    )


# ========== Фикстуры для логирования ==========

@pytest.fixture(autouse=True)
def log_test_info(request):
    """Автоматическое логирование информации о тесте."""
    test_name = request.node.name
    with allure.step(f'Запуск теста: {test_name}'):
        print(f"\n{'='*60}")
        print(f"Запуск теста: {test_name}")
        print(f"{'='*60}")
    
    yield
    
    with allure.step(f'Завершение теста: {test_name}'):
        print(f"\n{'='*60}")
        print(f"Завершение теста: {test_name}")
        print(f"{'='*60}")
