import numpy as np
import os
from scipy.interpolate import interp1d

from Code.core.base_structure import BaseStructure
from Code.core.utils import cond, diel1, CalMat, SaveRes
from Code.config import JSON_PATH

class NewStructure(BaseStructure):
    def get_w_list(self) -> list:
        return [self.config["W1"]]

    def process_parameters(self, npy_path: str, freq_range: np.ndarray) -> dict:
        # Специфичная логика
        pass

    def run_talgat(self, current_run: str) -> None:
        # Специфичная логика
        pass