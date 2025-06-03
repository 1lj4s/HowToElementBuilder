import json
import os
from typing import Any

class SimulationConfigBuilder:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.data = {}
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                try:
                    self.data = json.load(f)
                except json.JSONDecodeError:
                    self.data = {}

    def add_structure(self, struct_name: str, **params: Any):
        """Добавляет параметры структуры в конфигурацию."""
        self.data[struct_name] = params

    def get_structure(self, struct_name: str) -> dict:
        """Возвращает параметры структуры по имени."""
        return self.data.get(struct_name, {})

    def validate_structure(self, struct_name: str, required_params: set) -> bool:
        """Проверяет наличие обязательных параметров для структуры."""
        if struct_name not in self.data:
            print(f"Ошибка: структура {struct_name} не найдена в конфигурации")
            return False
        missing = required_params - set(self.data[struct_name].keys())
        if missing:
            print(f"Ошибка: отсутствуют параметры {missing} для структуры {struct_name}")
            return False
        return True

    def save(self):
        """Сохраняет конфигурацию в JSON-файл."""
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        with open(self.json_path, 'w') as f:
            json.dump(self.data, f, indent=2)