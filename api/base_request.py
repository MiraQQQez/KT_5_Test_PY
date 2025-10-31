import requests
import pprint
from typing import Optional, Dict, Any


class BaseRequest:
    """
    Базовый класс для работы с API.
    Предоставляет методы для выполнения HTTP запросов.
    """

    def __init__(self, base_url: str):
        """
        Инициализация базового класса для работы с API.
        
        Args:
            base_url (str): Базовый URL API
        """
        self.base_url = base_url
        self.session = requests.Session()
        # Можно добавить заголовки, авторизацию и т.д.
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _request(self, url: str, request_type: str, data: Optional[Dict] = None, 
                 json_data: Optional[Dict] = None, expected_error: bool = False) -> requests.Response:
        """
        Выполняет HTTP запрос указанного типа.
        
        Args:
            url (str): URL для запроса
            request_type (str): Тип запроса (GET, POST, PUT, DELETE)
            data (Optional[Dict]): Данные для отправки (форма data)
            json_data (Optional[Dict]): Данные для отправки (JSON)
            expected_error (bool): Ожидается ли ошибка
            
        Returns:
            requests.Response: Ответ от сервера
        """
        response = None
        
        try:
            if request_type == 'GET':
                response = self.session.get(url)
            elif request_type == 'POST':
                response = self.session.post(url, data=data, json=json_data)
            elif request_type == 'PUT':
                response = self.session.put(url, data=data, json=json_data)
            elif request_type == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Неподдерживаемый тип запроса: {request_type}")
            
            # Логирование запроса и ответа
            self._log_request(request_type, response)
            
            # Проверка статуса
            if not expected_error:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            if not expected_error:
                print(f"Ошибка при выполнении запроса: {e}")
            
        return response

    def _log_request(self, request_type: str, response: requests.Response):
        """
        Логирует информацию о запросе и ответе.
        
        Args:
            request_type (str): Тип запроса
            response (requests.Response): Ответ от сервера
        """
        print(f'\n{"="*50}')
        print(f'{request_type} запрос')
        print(f'URL: {response.url}')
        print(f'Status Code: {response.status_code}')
        print(f'Reason: {response.reason}')
        
        try:
            print(f'Response JSON:')
            pprint.pprint(response.json())
        except:
            print(f'Response Text: {response.text}')
        
        print(f'{"="*50}\n')

    def get(self, endpoint: str, endpoint_id: Optional[str] = None, 
            expected_error: bool = False) -> Any:
        """
        Выполняет GET запрос.
        
        Args:
            endpoint (str): Конечная точка API
            endpoint_id (Optional[str]): ID ресурса
            expected_error (bool): Ожидается ли ошибка
            
        Returns:
            Any: Ответ в формате JSON
        """
        url = f'{self.base_url}/{endpoint}'
        if endpoint_id:
            url += f'/{endpoint_id}'
        
        response = self._request(url, 'GET', expected_error=expected_error)
        
        try:
            return response.json()
        except:
            return response.text

    def post(self, endpoint: str, json_data: Dict, endpoint_id: Optional[str] = None) -> Any:
        """
        Выполняет POST запрос.
        
        Args:
            endpoint (str): Конечная точка API
            json_data (Dict): Данные для отправки
            endpoint_id (Optional[str]): ID ресурса
            
        Returns:
            Any: Ответ в формате JSON
        """
        url = f'{self.base_url}/{endpoint}'
        if endpoint_id:
            url += f'/{endpoint_id}'
        
        response = self._request(url, 'POST', json_data=json_data)
        
        try:
            return response.json()
        except:
            return response.text

    def put(self, endpoint: str, json_data: Dict, endpoint_id: Optional[str] = None) -> Any:
        """
        Выполняет PUT запрос.
        
        Args:
            endpoint (str): Конечная точка API
            json_data (Dict): Данные для обновления
            endpoint_id (Optional[str]): ID ресурса
            
        Returns:
            Any: Ответ в формате JSON
        """
        url = f'{self.base_url}/{endpoint}'
        if endpoint_id:
            url += f'/{endpoint_id}'
        
        response = self._request(url, 'PUT', json_data=json_data)
        
        try:
            return response.json()
        except:
            return response.text

    def delete(self, endpoint: str, endpoint_id: str, expected_error: bool = False) -> Any:
        """
        Выполняет DELETE запрос.
        
        Args:
            endpoint (str): Конечная точка API
            endpoint_id (str): ID ресурса для удаления
            expected_error (bool): Ожидается ли ошибка
            
        Returns:
            Any: Ответ в формате JSON
        """
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'DELETE', expected_error=expected_error)
        
        try:
            return response.json()
        except:
            return response.text