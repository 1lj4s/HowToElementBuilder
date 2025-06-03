from abc import ABC, abstractmethod
from Code.core.base_structure import BaseStructure

class BaseSimulation(ABC):
    def __init__(self, structure: BaseStructure, current_run: str):
        self.structure = structure
        self.current_run = current_run

    @abstractmethod
    def run(self) -> None:
        """Запускает симуляцию."""
        pass