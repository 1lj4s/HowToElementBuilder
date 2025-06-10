import numpy as np
import os
import logging
from Code.core.base_structure import BaseStructure
from Code.config import FILES_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MOPEN(BaseStructure):
    def get_w_list(self) -> list:
        """Возвращает список ширин (W) для структуры."""
        return [self.config["W"]]

    def process_parameters(self, npy_path: str, freq_range: np.ndarray) -> dict:
        """Для CustomCir с .cir файлом обработка параметров не требуется."""
        logger.info(
            f"Обработка параметров для MOPEN не требуется, используется .cir файл: {self.config['result_path']}")
        return {}

    def _generate_talgat_specific_script(self, current_run: str, W: float) -> str:
        """Talgat-скрипт для MOPEN не требуется для CustomCir."""
        logger.info("Talgat-скрипт для MOPEN не требуется для CustomCir")
        return ""