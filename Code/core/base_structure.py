# Code/core/base_structure.py
from abc import ABC, abstractmethod
import numpy as np
import os
import logging
import subprocess
from Code.input.input import SimulationConfigBuilder
from Code.config import FILES_DIR, JSON_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseStructure(ABC):
    def __init__(self, struct_name: str, config_path: str = JSON_PATH):
        self.struct_name = struct_name
        self.config_builder = SimulationConfigBuilder(config_path)
        self.config = self.config_builder.get_structure(struct_name)
        required_params = {"f0", "length", "Z0", "num_ports"}
        if not self.config_builder.validate_structure(struct_name, required_params):
            raise ValueError(f"Некорректная конфигурация для {struct_name}")
        self.num_ports = self.config.get("num_ports", 2)

    @abstractmethod
    def get_w_list(self) -> list:
        """Возвращает список ширин (W) для структуры."""
        pass

    @abstractmethod
    def process_parameters(self, npy_path: str, freq_range: np.ndarray) -> dict:
        """Обрабатывает параметры для RLGC -> S преобразования."""
        pass

    @abstractmethod
    def _generate_talgat_specific_script(self, current_run: str, W: float) -> str:
        """Генерирует специфичную часть Talgat-скрипта для структуры."""
        pass

    def _get_common_talgat_script(self) -> str:
        """Возвращает общую часть Talgat-скрипта (импорты и функции)."""
        COND_CODE = """
def cond(X, Y, W, T, D1, D2, TOP, GND):
    if TOP:
        c = 1.
        a = 0.
        na = 1.
    else:
        c = -1.
        a = 1.
        na = 0.
    if GND:
        CONDUCTOR_GROUNDED()
    else:
        CONDUCTOR()
    SET_ER_PLUS(D1[0])
    SET_MU_PLUS(D1[1])
    SET_TAN_DELTA_PLUS(D1[2])
    LINE(X + a * W, Y, X + na * W, Y)
    SET_ER_PLUS(D2[0])
    SET_MU_PLUS(D2[1])
    SET_TAN_DELTA_PLUS(D2[2])
    LINETO(X + na * W, Y + c * T)
    LINETO(X + a * W, Y + c * T)
    LINETO(X + a * W, Y)
    return [X, W]
"""

        DIEL1_CODE = """
def diel1(A, H, D1, D0):
    N = len(A)
    DIELECTRIC()
    SET_ER_PLUS(D1[0])
    SET_MU_PLUS(D1[1])
    SET_TAN_DELTA_PLUS(D1[2])
    SET_ER_MINUS(D0[0])
    SET_MU_MINUS(D0[1])
    SET_TAN_DELTA_MINUS(D0[2])
    LINE(0, H, A[0][0], H)
    LINE(A[N-1][0] + A[N-1][1], H, A[N-1][0] + A[N-1][1] + A[0][0], H)
    if N >= 2:
        for i1 in range(N-1):
            LINE(A[i1][0] + A[i1][1], H, A[i1+1][0], H)
"""

        CALMAT_CODE = """
def CalMat(conf, f0, loss=False, sigma=None):
    smn_L = SMN_L_OMP(conf)
    mL = CALCULATE_L(smn_L, conf)
    if loss:
        smn_CG = SMN_CG_OMP(conf)
        mC = CALCULATE_C(SMN_C_OMP(conf), conf)
        n = GET_MATRIX_ROWS(mL)
        mR_arr = np.zeros((n, n, len(f0)))
        mG_arr = np.zeros((n, n, len(f0)))
        for idx in range(len(f0)):
            freq = f0[idx]
            mR = CALCULATE_R(smn_L, conf, freq, sigma)
            cg = CALCULATE_CG(smn_CG, conf, freq)
            mG = GET_IMAG_MATRIX(cg)
            for i in range(n):
                for j in range(n):
                    mR_arr[i, j, idx] = GET_MATRIX_VALUE(mR, i, j)
                    mG_arr[i, j, idx] = GET_MATRIX_VALUE(mG, i, j)
    else:
        mC = CALCULATE_C(SMN_C_OMP(conf), conf)
        n = GET_MATRIX_ROWS(mL)
        mR_arr = np.zeros((n, n, 1))
        mG_arr = np.zeros((n, n, 1))
    mL_arr = np.zeros((n, n))
    mC_arr = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            mL_arr[i, j] = GET_MATRIX_VALUE(mL, i, j)
            mC_arr[i, j] = GET_MATRIX_VALUE(mC, i, j)
    return {
        'mL': mL_arr,
        'mC': mC_arr,
        'mR': mR_arr,
        'mG': mG_arr
    }
"""

        SAVERES_CODE = """
def SaveRes(path, data_dict):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    if not path.endswith(".npy"):
        path += ".npy"
    np.save(path, data_dict)
    print(f"[!] Result saved to: {path}")
"""

        return f"""
register_talgat_commands()
INCLUDE("UTIL")
INCLUDE("RESPONSE")
INCLUDE("MATRIX")
INCLUDE("MOM2D")
INCLUDE("TLX")
INCLUDE("INFIX")
INCLUDE("GRAPH")
import numpy as np
import os

{COND_CODE}
{DIEL1_CODE}
{CALMAT_CODE}
{SAVERES_CODE}
"""

    def run_talgat(self, current_run: str) -> None:
        """Запускает Talgat для структуры."""
        for W in self.get_w_list():
            # Генерируем общую и специфичную части скрипта
            common_script = self._get_common_talgat_script()
            specific_script = self._generate_talgat_specific_script(current_run, W)
            script = common_script + specific_script

            temp_script_path = os.path.join(FILES_DIR, "ts", f"{self.struct_name}_run.py")
            try:
                os.makedirs(os.path.dirname(temp_script_path), exist_ok=True)
                with open(temp_script_path, 'w', encoding='utf-8') as f:
                    f.write(script)
                logger.info(f"Временный скрипт Talgat создан: {temp_script_path}")
            except Exception as e:
                logger.error(f"Ошибка при создании скрипта {temp_script_path}: {e}")
                continue

            # Запуск Talgat
            interpreter_path = r"C:\Program Files\TALGAT 2021\PythonClient.exe"
            if not os.path.exists(interpreter_path):
                logger.error(f"Talgat интерпретатор не найден: {interpreter_path}")
                continue

            try:
                exec_command = f"exec(open(r'''{temp_script_path}''').read())\n"
                process = subprocess.Popen(
                    [interpreter_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=False
                )
                stdout, stderr = process.communicate(input=exec_command.encode('utf-8'))
                logger.info(f"Talgat stdout:\n{stdout.decode('utf-8', errors='replace')}")
                if stderr:
                    logger.warning(f"Talgat stderr:\n{stderr.decode('utf-8', errors='replace')}")
            except Exception as e:
                logger.error(f"Ошибка при запуске Talgat: {e}")