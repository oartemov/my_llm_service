import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from services.file_cache import get_from_cache, save_to_cache, _get_cache_dir


class TestRecipeGenerator:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def valid_request(self):
        return {"dish": "Борщ", "output_format": "Список + шаги", "people": 4}

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        cache_dir = _get_cache_dir()
        for f in cache_dir.glob("*.json"):
            f.unlink()
        yield

    def test_valid_request_returns_200(self, client, valid_request):
        with patch("services.model.call_llm") as mock_call:
            mock_call.return_value = "Список продуктов"
            response = client.post("/api/chat", json=valid_request)

            assert response.status_code == 200
            data = response.json()
            assert "recipe" in data
            assert data["recipe"] == "Список продуктов"

    def test_invalid_dish_too_short(self, client):
        response = client.post("/api/chat", json={
            "dish": "Бо",
            "output_format": "Список продуктов",
            "people": 2
        })
        assert response.status_code == 422

    def test_invalid_dish_too_long(self, client):
        response = client.post("/api/chat", json={
            "dish": "Б" * 101,
            "output_format": "Список продуктов",
            "people": 2
        })
        assert response.status_code == 422

    def test_invalid_people_too_small(self, client):
        response = client.post("/api/chat", json={
            "dish": "Борщ",
            "output_format": "Список продуктов",
            "people": 0
        })
        assert response.status_code == 422

    def test_invalid_people_too_large(self, client):
        response = client.post("/api/chat", json={
            "dish": "Борщ",
            "output_format": "Список продуктов",
            "people": 7
        })
        assert response.status_code == 422

    def test_invalid_output_format(self, client):
        response = client.post("/api/chat", json={
            "dish": "Борщ",
            "output_format": "Неверный формат",
            "people": 2
        })
        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        response = client.post("/api/chat", json={"dish": "Борщ"})
        assert response.status_code == 422

    def test_llm_failure_returns_500(self, client, valid_request):
        with patch("services.model.call_llm") as mock_call:
            mock_call.side_effect = Exception("API error")
            response = client.post("/api/chat", json=valid_request)

            assert response.status_code == 500
            assert "API error" in response.json()["detail"]

    def test_repeated_request_uses_cache(self, client, valid_request):
        with patch("services.model.call_llm") as mock_call:
            mock_call.return_value = "Список продуктов"

            client.post("/api/chat", json=valid_request)
            assert mock_call.call_count == 1

            client.post("/api/chat", json=valid_request)
            assert mock_call.call_count == 1

    def test_invalid_dish_empty_string(self, client):
        response = client.post("/api/chat", json={
            "dish": "",
            "output_format": "Список продуктов",
            "people": 2
        })
        assert response.status_code == 422

    def test_cache_miss_then_hit(self, client, valid_request):
        with patch("services.model.call_llm") as mock_call:
            mock_call.return_value = "Список продуктов"

            result1 = client.post("/api/chat", json=valid_request)
            assert result1.status_code == 200

            mock_call.return_value = "Другой результат"
            result2 = client.post("/api/chat", json=valid_request)
            assert result2.status_code == 200
            assert result2.json()["recipe"] == "Список продуктов"