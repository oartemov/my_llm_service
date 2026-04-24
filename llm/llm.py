import os
import time
from pathlib import Path
from typing import Tuple, Optional
import requests
import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.yaml"

def _load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

config = _load_config()

class GigaChatClient:
    def __init__(self):
        gigachat_config = config.get("gigachat", {})
        self.auth_url = gigachat_config.get("auth_url") 
        self.api_url = gigachat_config.get("api_url")
        self.credentials = gigachat_config.get("credentials") or os.getenv("GIGACHAT_CREDENTIALS")
        self.api_key = gigachat_config.get("api_key") or os.getenv("GIGACHAT_API_KEY")
        self.access_token = None
        self.token_expires_at = 0

    def _get_token(self) -> Tuple[Optional[str], Optional[str]]:
        """Получение токена доступа"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token, None
        
        headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': '106266bb-e55f-42e7-a29b-3d3700d885af',
        }
        
        if self.credentials:
            import base64
            headers["Authorization"] = f"Basic {self.credentials}"
            data = {"scope": "GIGACHAT_API_PERS"}
        elif self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            data = {}
        else:
            return None, "Не настроены учетные данные для GigaChat"
        
        try:
            response = requests.request("POST", self.auth_url, headers=headers, data=data, verify=False)
           
            if response.status_code != 200:
                return None, f"Ошибка авторизации: {response.status_code}"
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = time.time() + expires_in - 300
            
            return self.access_token, None
            
        except requests.exceptions.Timeout:
            return None, "Таймаут при авторизации"
        except Exception as e:
            return None, f"Ошибка подключения: {str(e)}"
    
    def generate_shopping_list(self, prompt: str) -> Tuple[str, Optional[str]]:
        """Генерация списка покупок. Возвращает (результат, ошибка)."""
        token, error = self._get_token()
        if error:
            return "", error
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        payload = {
            "model": "GigaChat",
            "messages": [{"role": "system", "content": "Ты помощник."}, 
                         {"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        max_retries = 3
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, verify=False, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if not content or len(content.strip()) < 10:
                        return "", "Пустой ответ модели."
                    return content.strip(), None
                elif 400 <= response.status_code < 500:
                    return "", "Не настроен доступ к сервису."
                elif 500 <= response.status_code < 600:
                    if attempt < max_retries:
                        time.sleep(1)
                        continue
                    return "", "Сервис временно недоступен."
                else:
                    return "", f"Ошибка API: {response.status_code}"
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                return "", "Таймаут."
            except requests.exceptions.ConnectionError:
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                return "", "Ошибка соединения."
            except Exception as e:
                return "", f"Ошибка: {str(e)}"

        return "", "Не удалось получить ответ."