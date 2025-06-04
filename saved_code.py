
# ===== File: config.py =====

import os
import numpy as np

from Code.input.input import SimulationConfigBuilder

# Константы
FILES_DIR = os.path.join(os.path.dirname(__file__), "Files")
JSON_PATH = os.path.join(FILES_DIR, "json", "simulation_config.json")
FREQUENCY_RANGE = np.arange(0.1e9, 40.e9, 0.1e9)

# Доступные структуры и симуляции
AVAILABLE_STRUCTURES = ["MLIN", "MTAPER", "MXOVER"]
AVAILABLE_SIMULATIONS = ["sym_sub_test", "sym_snp_test"]

# Создание конфигурации
def create_default_config():
    builder = SimulationConfigBuilder(JSON_PATH)
    builder.add_structure(
        struct_name="MSUB",
        sigma=None,  #
        ER0=1.0,  #
        MU0=1.0,  #
        TD0=0.0,  #
        ER1=9.7,  #
        MU1=1.0001,  #
        TD1=0.003,  #
        ER2=3.,  #
        MU2=1.0002,  #
        TD2=0.001,  #
        T=5.1e-6,  #
        H=100.e-6,  #
        H1=100.e-6  # для mxover

    )
    builder.add_structure(
        struct_name="SIM",
        f0=[0.1e9, 0.5e9, 1.e9, 5.e9, 10.e9, 20.e9, 30.e9, 40.e9], ## диапазон частот для моделирования с потерями
        seg_cond=3.0, ##
        seg_diel=1.0, ##
        loss=True, ##
        Z0=50, ##

    )
    builder.add_structure(
        struct_name="MLIN",
        result_path=os.path.join(FILES_DIR, "npy", "MLIN_test.npy"),
        W1=10.e-6,
        length=0.01,
        num_ports=2

    )
    builder.add_structure(
        struct_name="MTAPER",
        result_path=os.path.join(FILES_DIR, "npy", "MTAPER_test.npy"),
        W1=10.e-6,
        W2=100.e-6,
        Wtype="lin",
        length=0.01,
        num_ports = 2
    )
    builder.add_structure(
        struct_name="MXOVER",
        result_path=os.path.join(FILES_DIR, "npy", "MTAPER_test.npy"),
        W1=50.e-6,
        W2=50.e-6,
        length=0.01,
        num_ports=4
    )
    builder.save()

# ===== File: main.py =====

from Code.config import AVAILABLE_STRUCTURES, AVAILABLE_SIMULATIONS, JSON_PATH, create_default_config
from Code.structures.mlin import MLIN
from Code.structures.mtaper import MTAPER
from Code.structures.mxover import MXOVER
from Code.simulations.sym_sub_test import SymSubTest
from Code.simulations.sym_snp_test import SymSnpTest

def main():
    structure_name = "MLIN"  # Или "MLIN", "MTAPER", "MXOVER"
    simulation_type = "sym_snp_test"  # Или "sym_sub_test"
    current_run = "test"

    # Создание конфигурации
    create_default_config()

    # Выбор структуры
    if structure_name == "MLIN":
        structure = MLIN(structure_name, JSON_PATH)
    elif structure_name == "MTAPER":
        structure = MTAPER(structure_name, JSON_PATH)
    elif structure_name == "MXOVER":
        structure = MXOVER(structure_name, JSON_PATH)
    else:
        raise ValueError(f"Структура {structure_name} не поддерживается. Доступные структуры: {AVAILABLE_STRUCTURES}")

    # Выбор симуляции
    if simulation_type == "sym_sub_test":
        simulation = SymSubTest(structure, current_run)
    elif simulation_type == "sym_snp_test":
        simulation = SymSnpTest(structure, current_run)
    else:
        raise ValueError(f"Тип симуляции {simulation_type} не поддерживается. Доступные симуляции: {AVAILABLE_SIMULATIONS}")

    # Запуск симуляции
    simulation.run()

if __name__ == "__main__":
    main()

# ===== File: connectors\connector.py =====

import skrf
import os
import logging
from Code.converters.saver import save_ntwk
from Code.config import FILES_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_elements(ntwk_list, struct_name, current_run, connection_type="series"):
    """
    Объединяет список объектов Network в один (серийно или параллельно) и сохраняет результат.

    Args:
        ntwk_list: Список объектов skrf.Network.
        struct_name: Название структуры (например, 'MLIN', 'MTAPER').
        current_run: Имя текущего запуска (например, 'test').
        connection_type: Тип соединения ('series' или 'parallel').

    Returns:
        Объединенный объект skrf.Network или None, если список пуст.
    """
    if not ntwk_list:
        logger.warning("Нет доступных Network объектов для объединения.")
        return None

    try:
        combined = ntwk_list[0]
        if connection_type == "series":
            for ntwk in ntwk_list[1:]:
                combined = combined ** ntwk
        elif connection_type == "parallel":
            logger.warning("Параллельное соединение пока не реализовано.")
            # Реализация параллельного соединения (если потребуется)
            return None
        else:
            raise ValueError(f"Тип соединения {connection_type} не поддерживается")

        snp_dir = os.path.join(FILES_DIR, "snp")
        save_ntwk(combined, snp_dir, struct_name, current_run)
        logger.info(f"Объединенная сеть сохранена для {struct_name}_{current_run}")
        return combined

    except Exception as e:
        logger.error(f"Ошибка при объединении сетей: {e}")
        return None

# ===== File: converters\converter.py =====

import numpy as np
from scipy.linalg import eig, inv


def rlgc2s_t(resistance, inductance, conductance, capacitance, linelength, freq, z0):
    """
    Converts RLGC-parameters of transmission lines to S-parameters
    """
    # 0 Input validation
    if not np.isscalar(z0):
        raise ValueError("Z0 must be a scalar")
    if np.isnan(z0) or np.isinf(z0):
        raise ValueError("Z0 cannot be NaN or Inf")
    if np.any(np.imag(z0) != 0):
        raise ValueError("Z0 cannot be complex")

    freq = np.asarray(freq)
    freqpts = freq.size
    num_lines = resistance.shape[0]

    # Initialize output arrays
    s_params = np.zeros((2 * num_lines, 2 * num_lines, freqpts), dtype=complex)
    z0_matrix = z0 * np.eye(2 * num_lines)

    # For each frequency point
    for freqidx in range(freqpts):
        # Extract RLGC matrices for this frequency
        R = resistance[:, :, freqidx] if resistance.ndim == 3 else resistance
        L = inductance[:, :, freqidx] if inductance.ndim == 3 else inductance
        G = conductance[:, :, freqidx] if conductance.ndim == 3 else conductance
        C = capacitance[:, :, freqidx] if capacitance.ndim == 3 else capacitance

        # Per-unit-length impedance and admittance
        Z = R + 1j * 2 * np.pi * freq[freqidx] * L
        Y = G + 1j * 2 * np.pi * freq[freqidx] * C

        # Eigen decomposition of Z*Y
        D, V = eig(Z @ Y)
        gammaEig = np.sqrt(D)  # propagation constants

        # Calculate gamma matrix
        gamma = V @ np.diag(gammaEig) @ inv(V)

        # Characteristic impedance matrix
        Zc = inv(gamma) @ Z

        # Hyperbolic functions of gamma*length
        cosh_gammaL = V @ np.diag(np.cosh(gammaEig * linelength)) @ inv(V)
        sinh_gammaL = V @ np.diag(np.sinh(gammaEig * linelength)) @ inv(V)

        # ABCD parameters
        A = cosh_gammaL
        B = sinh_gammaL @ Zc
        C = inv(Zc) @ sinh_gammaL
        D = inv(Zc) @ cosh_gammaL @ Zc

        # Z-parameters
        Cinv = inv(C)
        Z11 = A @ Cinv
        Z12 = Z11 @ D - B
        Z21 = Cinv
        Z22 = Z21 @ D

        # Combine Z-parameters
        Z_params = np.block([
            [Z11, Z12],
            [Z21, Z22]
        ])

        # Convert to S-parameters
        s_params[:, :, freqidx] = (Z_params - z0_matrix) @ inv(Z_params + z0_matrix)

    # Prepare output struct
    rlgc_struct = {
        'R': resistance,
        'L': inductance,
        'G': conductance,
        'C': capacitance,
        'Zc': Zc if freqpts == 1 else np.repeat(Zc[:, :, np.newaxis], freqpts, axis=2),
        'gamma': gamma if freqpts == 1 else np.repeat(gamma[:, :, np.newaxis], freqpts, axis=2)
    }

    return s_params, rlgc_struct

# ===== File: converters\rlcg2s.py =====

import numpy as np
import os
import logging
from glob import glob

from Code.converters.saver import save_to_snp
from Code.converters.converter import rlgc2s_t
from Code.core.utils import get_config
from Code.config import FILES_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_matching_files(npy_dir: str, struct_name: str, current_run: str) -> list:
    pattern = os.path.join(npy_dir, f"{struct_name}_{current_run}_*.npy")
    logger.info(f"Поиск файлов по шаблону: {pattern}")
    files = glob(pattern)
    logger.info(f"Найдено файлов: {len(files)} ({files})")
    return files

def run_rlcg2s(structure, current_run: str, return_networks: bool = False) -> list:
    npy_dir = os.path.join(FILES_DIR, "npy")
    snp_dir = os.path.join(FILES_DIR, "snp")
    freq_range = np.arange(0.1e9, 40.e9, 0.1e9)

    logger.info(f"Директория для .npy: {npy_dir}")
    logger.info(f"Директория для .snp: {snp_dir}")

    os.makedirs(snp_dir, exist_ok=True)
    matching_files = find_matching_files(npy_dir, structure.struct_name, current_run)

    if not matching_files:
        logger.error(f"Не найдено файлов для {structure.struct_name}_{current_run}_*.npy в {npy_dir}")
        return []

    results = []
    for npy_path in matching_files:
        logger.info(f"Обработка файла: {os.path.basename(npy_path)}")
        params = structure.process_parameters(npy_path, freq_range)
        if not params:
            logger.error(f"Не удалось обработать параметры для {npy_path}")
            continue

        try:
            s_params, rlgc_struct = rlgc2s_t(
                params['mR'], params['mL'], params['mG'], params['mC'],
                params['length'], freq_range, params['Z0']
            )
            W_str = os.path.basename(npy_path).split('_')[-1].split('.')[0]
            snp_filename = f"{structure.struct_name}_{current_run}_{W_str}.s{s_params.shape[1]}p"
            snp_path = os.path.join(snp_dir, snp_filename)
            mode = 'save' if not return_networks else 'return'

            ntwk = save_to_snp(s_params, freq_range, snp_path, mode=mode)
            if return_networks and ntwk:
                results.append(ntwk)
        except Exception as e:
            logger.error(f"Ошибка при сохранении {snp_path}: {e}")

    logger.info(f"Обработка завершена. Успешно обработано {len(results)} файлов.")
    return results if return_networks else None

# ===== File: converters\saver.py =====

import numpy as np
import skrf
import os

def save_to_snp(s_params, freq, filename, mode='save'):
    """
    Сохраняет S-параметры в файл формата Touchstone (.sNp для N-портовых систем).
    """
    n_ports = s_params.shape[0]
    expected_ext = f'.s{n_ports}p'

    # Обновляем имя файла с правильным расширением
    base, ext = os.path.splitext(filename)
    if ext.lower() != expected_ext:
        print(f"Предупреждение: ожидалось расширение {expected_ext}, получено {ext}")
        filename = base + expected_ext

    # Переставляем оси: (n, n, M) -> (M, n, n)
    s = np.moveaxis(s_params, 2, 0)

    # Создаем объект Frequency и Network
    frequency = skrf.Frequency.from_f(freq, unit='Hz')
    ntwk = skrf.Network(frequency=frequency, s=s, name=os.path.basename(base))

    if mode == 'save':
        ntwk.write_touchstone(filename=base)
        print(f"Файл {filename} успешно сохранён")
        return None
    elif mode == 'return':
        return ntwk
    else:
        raise ValueError("mode must be either 'save' or 'return'")

def save_ntwk(ntwk, directory, struct_name, current_run):
    """
    Сохраняет Network объект в файл Touchstone в указанную директорию
    с именем struct_name_current_run.sNp.
    """
    os.makedirs(directory, exist_ok=True)
    num_ports = ntwk.number_of_ports
    filename = f"{struct_name}_{current_run}.s{num_ports}p"
    filepath = os.path.join(directory, filename)

    # ✔️ Надёжное удаление расширения
    filepath_no_ext, _ = os.path.splitext(filepath)

    ntwk.write_touchstone(filepath_no_ext)
    print(f"Сохранён объединённый файл: {filepath}")

# ===== File: core\base_structure.py =====

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

        # Специфичные параметры валидации для разных структур
        if struct_name in ["MLIN", "MTAPER"]:
            required_params = {"length", "W1"}
        elif struct_name == "MXOVER":
            required_params = {"length", "W1", "W2", "num_ports"}
        elif struct_name == "MSUB":
            required_params = {"ER0", "MU0", "TD0", "ER1", "MU1", "TD1", "T", "H"}
        elif struct_name == "SIM":
            required_params = {"f0", "Z0", "num_ports"}
        else:
            required_params = set()

        if not self.config_builder.validate_structure(struct_name, required_params):
            raise ValueError(f"Некорректная конфигурация для {struct_name}")

        # Загружаем параметры SIM и MSUB
        self.sim_config = self.config_builder.get_structure("SIM")
        self.msub_config = self.config_builder.get_structure("MSUB")
        self.num_ports = self.config.get("num_ports", self.sim_config.get("num_ports", 2))

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

# ===== File: core\simulation.py =====

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

# ===== File: core\utils.py =====

import numpy as np
import os
import json
from scipy.interpolate import interp1d

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
    LINE(A[N - 1][0] + A[N - 1][1], H, A[N - 1][0] + A[N - 1][1] + A[0][0], H)
    if N >= 2:
        for i1 in range(N - 1):
            LINE(A[i1][0] + A[i1][1], H, A[i1 + 1][0], H)

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

def SaveRes(path, data_dict):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    if not path.endswith(".npy"):
        path += ".npy"
    np.save(path, data_dict)
    print(f"[!] Result saved to: {path}")

def get_config(config_path: str) -> dict:
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке JSON файла: {e}")
        return {}
        return {}

# ===== File: Files\ts\MLIN_run.py =====


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


def SaveRes(path, data_dict):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    if not path.endswith(".npy"):
        path += ".npy"
    np.save(path, data_dict)
    print(f"[!] Result saved to: {path}")


W = 1e-05
result_path = r'D:\saves\Pycharm\HowToElementBuilder\Code\Files\npy\MLIN_test_10.npy'
f0 = [100000000.0, 500000000.0, 1000000000.0, 5000000000.0, 10000000000.0, 20000000000.0, 30000000000.0, 40000000000.0]
seg_cond = 3.0
seg_diel = 1.0
loss = True
sigma = None
ER0 = 1.0
MU0 = 1.0
TD0 = 0.0
ER1 = 9.7
MU1 = 1.0001
TD1 = 0.003
T = 5.1e-06
H = 0.0001
D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
CC1.append(cond(2 * W, H, W, T, D1, D0, True, False))
diel1(CC1, H, D1, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
SaveRes(result_path, result)


# ===== File: Files\ts\MTAPER_run.py =====


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


def SaveRes(path, data_dict):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    if not path.endswith(".npy"):
        path += ".npy"
    np.save(path, data_dict)
    print(f"[!] Result saved to: {path}")


W = 0.0001
result_path = r'D:\saves\Pycharm\HowToElementBuilder\Code\Files\npy\MTAPER_test_100.npy'
f0 = [100000000.0, 500000000.0, 1000000000.0, 5000000000.0, 10000000000.0, 20000000000.0, 30000000000.0, 40000000000.0]
seg_cond = 3.0
seg_diel = 1.0
loss = True
sigma = None
ER0 = 1.0
MU0 = 1.0
TD0 = 0.0
ER1 = 9.7
MU1 = 1.0001
TD1 = 0.003
T = 5.1e-06
H = 0.0001
D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
CC1.append(cond(2 * W, H, W, T, D1, D0, True, False))
diel1(CC1, H, D1, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
SaveRes(result_path, result)


# ===== File: Files\ts\MXOVER_run.py =====


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


def SaveRes(path, data_dict):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    if not path.endswith(".npy"):
        path += ".npy"
    np.save(path, data_dict)
    print(f"[!] Result saved to: {path}")


W1 = 5e-05
W2 = 5e-05
result_path = r'D:\saves\Pycharm\HowToElementBuilder\Code\Files\npy\MXOVER_test_50.npy'
f0 = [100000000.0, 500000000.0, 1000000000.0, 5000000000.0, 10000000000.0, 20000000000.0, 30000000000.0, 40000000000.0]
seg_cond = 3.0
seg_diel = 1.0
loss = True
sigma = None
ER0 = 1.0
MU0 = 1.0
TD0 = 0.0
ER1 = 9.7
MU1 = 1.0001
TD1 = 0.003
ER2 = 3.0
MU2 = 1.0002
TD2 = 0.001
T = 5.1e-06
H1 = 0.0001
H2 = 0.0001
D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]
D2 = [ER2, MU2, TD2]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
CC2 = []
CC1.append(cond(2*W1, H1, W1, T, D1, D2, True, False))
diel1(CC1, H1, D1, D2)
CC2.append(cond(2*W2, H1+H2, W2, T, D2, D0, True, False))
diel1(CC2, H1+H2, D2, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
SaveRes(result_path, result)


# ===== File: input\input.py =====

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

# ===== File: simulations\sym_snp_test.py =====

from Code.core.simulation import BaseSimulation
from Code.converters.rlcg2s import run_rlcg2s
from Code.converters.saver import save_ntwk
from Code.connectors.connector import connect_elements
from Code.symica.sym_spice import run_symspice


class SymSnpTest(BaseSimulation):
    def run(self) -> None:
        # Шаг 1: Запуск Talgat
        self.structure.run_talgat(self.current_run)

        # Шаг 2: Преобразование RLGC в S-параметры
        ntwk_list = run_rlcg2s(self.structure, self.current_run, return_networks=True)

        # Шаг 3: Соединение сетей
        if ntwk_list:
            combined_ntwk = connect_elements(ntwk_list, self.structure.struct_name, self.current_run)

        # Шаг 4: Запуск Symica с .snp файлом
        run_symspice("SymSnpTest")

# ===== File: simulations\sym_sub_test.py =====

from Code.core.simulation import BaseSimulation
from Code.converters.rlcg2s import run_rlcg2s
from Code.converters.saver import save_ntwk
from Code.connectors.connector import connect_elements
from Code.vector_fitting.vector_fitting import run_vector_fitting
from Code.symica.sym_spice import run_symspice


class SymSubTest(BaseSimulation):
    def run(self) -> None:
        # Шаг 1: Запуск Talgat
        self.structure.run_talgat(self.current_run)

        # Шаг 2: Преобразование RLGC в S-параметры
        ntwk_list = run_rlcg2s(self.structure, self.current_run, return_networks=True)

        # Шаг 3: Соединение сетей
        if ntwk_list:
            combined_ntwk = connect_elements(ntwk_list, self.structure.struct_name, self.current_run)

        # Шаг 4: Векторная аппроксимация
        run_vector_fitting(self.structure.struct_name, self.structure.num_ports)

        # Шаг 5: Запуск Symica
        run_symspice("SymSubTest")

# ===== File: structures\mlin.py =====

import numpy as np
import os
import logging
from scipy.interpolate import interp1d
from Code.core.base_structure import BaseStructure
from Code.config import FILES_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLIN(BaseStructure):
    def get_w_list(self) -> list:
        return [self.config["W1"]]

    def process_parameters(self, npy_path: str, freq_range: np.ndarray) -> dict:
        W_str = os.path.basename(npy_path).split('_')[-1].split('.')[0]
        try:
            W = float(W_str) / 1e6  # Конвертация в метры
        except ValueError:
            logger.error(f"Не удалось извлечь ширину из имени файла: {npy_path}")
            return {}

        length = self.config["length"]
        Z0 = self.sim_config["Z0"]
        f0 = self.sim_config["f0"]

        try:
            data = np.load(npy_path, allow_pickle=True).item()
        except Exception as e:
            logger.error(f"Ошибка при загрузке файла {npy_path}: {e}")
            return {}

        mL, mC, mR, mG = data['mL'], data['mC'], data['mR'], data['mG']
        M = len(freq_range)

        # Интерполяция mR и mG
        mR_interpolated = np.zeros((mR.shape[0], mR.shape[1], M))
        mG_interpolated = np.zeros((mG.shape[0], mG.shape[1], M))
        for i in range(mR.shape[0]):
            for j in range(mR.shape[1]):
                interp_func_R = interp1d(f0, mR[i, j, :], kind='linear', fill_value="extrapolate")
                interp_func_G = interp1d(f0, mG[i, j, :], kind='linear', fill_value="extrapolate")
                mR_interpolated[i, j, :] = interp_func_R(freq_range)
                mG_interpolated[i, j, :] = interp_func_G(freq_range)

        mL = np.repeat(mL[:, :, np.newaxis], M, axis=2)
        mC = np.repeat(mC[:, :, np.newaxis], M, axis=2)

        return {
            'mR': mR_interpolated,
            'mL': mL,
            'mG': mG_interpolated,
            'mC': mC,
            'length': length,
            'Z0': Z0
        }

    def _generate_talgat_specific_script(self, current_run: str, W: float) -> str:
        result_path = os.path.join(FILES_DIR, "npy", f"{self.struct_name}_{current_run}_{W * 1.e6:0g}.npy")
        sim_params = self.sim_config
        msub_params = self.msub_config

        return f"""
W = {W}
result_path = r'{result_path}'
f0 = {sim_params["f0"]}
seg_cond = {sim_params["seg_cond"]}
seg_diel = {sim_params["seg_diel"]}
loss = {sim_params["loss"]}
sigma = {msub_params.get("sigma", None)}
ER0 = {msub_params["ER0"]}
MU0 = {msub_params["MU0"]}
TD0 = {msub_params["TD0"]}
ER1 = {msub_params["ER1"]}
MU1 = {msub_params["MU1"]}
TD1 = {msub_params["TD1"]}
T = {msub_params["T"]}
H = {msub_params["H"]}
D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
CC1.append(cond(2 * W, H, W, T, D1, D0, True, False))
diel1(CC1, H, D1, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
SaveRes(result_path, result)
"""



# ===== File: structures\mtaper.py =====

import numpy as np
import os
import logging
from scipy.interpolate import interp1d
from Code.core.base_structure import BaseStructure
from Code.config import FILES_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MTAPER(BaseStructure):
    def get_w_list(self) -> list:
        W1 = self.config["W1"]
        W2 = self.config["W2"]
        Nsegs = self.config.get("Nsegs", 10)  # Значение по умолчанию
        Wtype = self.config.get("Wtype", "lin").lower()
        if Wtype == "log":
            return np.logspace(np.log10(W1), np.log10(W2), Nsegs).tolist()
        return np.linspace(W1, W2, Nsegs).tolist()

    def process_parameters(self, npy_path: str, freq_range: np.ndarray) -> dict:
        W_str = os.path.basename(npy_path).split('_')[-1].split('.')[0]
        try:
            W = float(W_str) / 1e6  # Конвертация в метры
        except ValueError:
            logger.error(f"Не удалось извлечь ширину из имени файла: {npy_path}")
            return {}

        length = self.config["length"]
        Nsegs = self.config.get("Nsegs", 10)
        Z0 = self.sim_config["Z0"]
        f0 = self.sim_config["f0"]
        segment_length = length / Nsegs

        try:
            data = np.load(npy_path, allow_pickle=True).item()
        except Exception as e:
            logger.error(f"Ошибка при загрузке файла {npy_path}: {e}")
            return {}

        mL, mC, mR, mG = data['mL'], data['mC'], data['mR'], data['mG']
        M = len(freq_range)

        mR_interpolated = np.zeros((mR.shape[0], mR.shape[1], M))
        mG_interpolated = np.zeros((mG.shape[0], mG.shape[1], M))
        for i in range(mR.shape[0]):
            for j in range(mR.shape[1]):
                interp_func_R = interp1d(f0, mR[i, j, :], kind='linear', fill_value="extrapolate")
                interp_func_G = interp1d(f0, mG[i, j, :], kind='linear', fill_value="extrapolate")
                mR_interpolated[i, j, :] = interp_func_R(freq_range)
                mG_interpolated[i, j, :] = interp_func_G(freq_range)

        mL = np.repeat(mL[:, :, np.newaxis], M, axis=2)
        mC = np.repeat(mC[:, :, np.newaxis], M, axis=2)

        return {
            'mR': mR_interpolated,
            'mL': mL,
            'mG': mG_interpolated,
            'mC': mC,
            'length': segment_length,
            'Z0': Z0
        }

    def _generate_talgat_specific_script(self, current_run: str, W: float) -> str:
        result_path = os.path.join(FILES_DIR, "npy", f"{self.struct_name}_{current_run}_{W * 1.e6:0g}.npy")
        sim_params = self.sim_config
        msub_params = self.msub_config

        return f"""
W = {W}
result_path = r'{result_path}'
f0 = {sim_params["f0"]}
seg_cond = {sim_params["seg_cond"]}
seg_diel = {sim_params["seg_diel"]}
loss = {sim_params["loss"]}
sigma = {msub_params.get("sigma", None)}
ER0 = {msub_params["ER0"]}
MU0 = {msub_params["MU0"]}
TD0 = {msub_params["TD0"]}
ER1 = {msub_params["ER1"]}
MU1 = {msub_params["MU1"]}
TD1 = {msub_params["TD1"]}
T = {msub_params["T"]}
H = {msub_params["H"]}
D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
CC1.append(cond(2 * W, H, W, T, D1, D0, True, False))
diel1(CC1, H, D1, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
SaveRes(result_path, result)
"""

# ===== File: structures\mxover.py =====

import numpy as np
import os
import logging
from scipy.interpolate import interp1d
from Code.core.base_structure import BaseStructure
from Code.config import FILES_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MXOVER(BaseStructure):
    def get_w_list(self) -> list:
        return [self.config["W1"], self.config["W2"]]

    def process_parameters(self, npy_path: str, freq_range: np.ndarray) -> dict:
        W_str = os.path.basename(npy_path).split('_')[-1].split('.')[0]
        try:
            W = float(W_str) / 1e6  # Конвертация в метры
        except ValueError:
            logger.error(f"Не удалось извлечь ширину из имени файла: {npy_path}")
            return {}

        length = self.config["length"]
        Z0 = self.sim_config["Z0"]
        f0 = self.sim_config["f0"]

        try:
            data = np.load(npy_path, allow_pickle=True).item()
        except Exception as e:
            logger.error(f"Ошибка при загрузке файла {npy_path}: {e}")
            return {}

        mL, mC, mR, mG = data['mL'], data['mC'], data['mR'], data['mG']
        M = len(freq_range)

        # Интерполяция mR и mG
        mR_interpolated = np.zeros((mR.shape[0], mR.shape[1], M))
        mG_interpolated = np.zeros((mG.shape[0], mG.shape[1], M))
        for i in range(mR.shape[0]):
            for j in range(mR.shape[1]):
                interp_func_R = interp1d(f0, mR[i, j, :], kind='linear', fill_value="extrapolate")
                interp_func_G = interp1d(f0, mG[i, j, :], kind='linear', fill_value="extrapolate")
                mR_interpolated[i, j, :] = interp_func_R(freq_range)
                mG_interpolated[i, j, :] = interp_func_G(freq_range)

        mL = np.repeat(mL[:, :, np.newaxis], M, axis=2)
        mC = np.repeat(mC[:, :, np.newaxis], M, axis=2)

        return {
            'mR': mR_interpolated,
            'mL': mL,
            'mG': mG_interpolated,
            'mC': mC,
            'length': length,
            'Z0': Z0
        }

    def _generate_talgat_specific_script(self, current_run: str, W: float) -> str:
        result_path = os.path.join(FILES_DIR, "npy", f"{self.struct_name}_{current_run}_{W * 1.e6:0g}.npy")
        sim_params = self.sim_config
        msub_params = self.msub_config
        W1 = self.config["W1"]
        W2 = self.config["W2"]

        return f"""
W1 = {W1}
W2 = {W2}
result_path = r'{result_path}'
f0 = {sim_params["f0"]}
seg_cond = {sim_params["seg_cond"]}
seg_diel = {sim_params["seg_diel"]}
loss = {sim_params["loss"]}
sigma = {msub_params.get("sigma", None)}
ER0 = {msub_params["ER0"]}
MU0 = {msub_params["MU0"]}
TD0 = {msub_params["TD0"]}
ER1 = {msub_params["ER1"]}
MU1 = {msub_params["MU1"]}
TD1 = {msub_params["TD1"]}
ER2 = {msub_params["ER2"]}
MU2 = {msub_params["MU2"]}
TD2 = {msub_params["TD2"]}
T = {msub_params["T"]}
H1 = {msub_params["H"]}
H2 = {msub_params["H1"]}
D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]
D2 = [ER2, MU2, TD2]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
CC2 = []
CC1.append(cond(2*W1, H1, W1, T, D1, D2, True, False))
diel1(CC1, H1, D1, D2)
CC2.append(cond(2*W2, H1+H2, W2, T, D2, D0, True, False))
diel1(CC2, H1+H2, D2, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
SaveRes(result_path, result)
"""

# ===== File: symica\sym_spice.py =====

import subprocess
import os
import shutil

def run_symspice(scs_file: str):
    base_dir = os.path.dirname(__file__)
    cir_path = os.path.abspath(os.path.join(base_dir, "..", "..", "Files", "sch", f"{scs_file}.scs"))
    cir_dir = os.path.dirname(cir_path)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    files_dir = os.path.join(project_root, "Files")
    output_dir = os.path.join(files_dir, "sym")
    expected_output = os.path.join(output_dir, f"{scs_file}.s2p")
    output_destination = os.path.join(output_dir, f"{scs_file}.s2p")

    if not os.path.exists(cir_path):
        raise FileNotFoundError(f"Файл {cir_path} не найден")

    os.makedirs(output_dir, exist_ok=True)
    command = ["symspice", os.path.basename(cir_path)]
    try:
        result = subprocess.run(command, cwd=cir_dir, capture_output=True, text=True, check=True)
        print("======= STDOUT =======")
        print(result.stdout)
        print("\n======= STDERR =======")
        print(result.stderr)
        if os.path.exists(expected_output):
            print(f"\n✅ Результат симуляции скопирован в: {output_destination}")
        else:
            print(f"\n⚠️ Выходной файл {expected_output} не найден. Симуляция могла не создать S-параметры.")
        print(f"\n✅ Симуляция {scs_file} завершена успешно.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при выполнении симуляции {scs_file}. Код ошибки: {e.returncode}")
        print("======= STDERR =======")
        print(e.stderr)
    except FileNotFoundError:
        print("\n❌ Ошибка: symspice не найден. Убедитесь, что он установлен и добавлен в PATH")

# ===== File: vector_fitting\vector_fitting.py =====

import skrf
import numpy as np
import matplotlib.pyplot as plt
import os
import logging
from Code.config import FILES_DIR, FREQUENCY_RANGE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_vector_fitting(struct_name: str, num_ports: int, show_plots: bool = True):
    """
    Выполняет векторную аппроксимацию (Vector Fitting) для создания SPICE-модели из S-параметров.

    Args:
        struct_name: Название структуры (например, 'MLIN', 'MTAPER').
        num_ports: Количество портов структуры.
        show_plots: Если True, отображает графики S-параметров.

    Returns:
        None
    """
    snp_path = os.path.join(FILES_DIR, "snp", f"{struct_name}_test.s{num_ports}p")
    cir_path = os.path.join(FILES_DIR, "cir", f"{struct_name}_test.cir")

    try:
        ntwk = skrf.Network(snp_path)
    except FileNotFoundError:
        logger.error(f"Файл {snp_path} не найден!")
        return

    try:
        vf = skrf.VectorFitting(ntwk)
        vf.auto_fit(
            n_poles_init_real=3,
            n_poles_init_cmplx=6,
            n_poles_add=5,
            model_order_max=100,
            iters_start=3,
            iters_inter=3,
            iters_final=5,
            target_error=0.01,
            alpha=0.03,
            gamma=0.03,
            nu_samples=1.0,
            parameter_type='s'
        )

        vf.write_spice_subcircuit_s(cir_path)
        logger.info(f"SPICE-модель сохранена в файл: {cir_path}")

        if show_plots:
            freq = FREQUENCY_RANGE
            plt.figure(figsize=(10, 8))
            for i in range(ntwk.nports):
                for j in range(ntwk.nports):
                    plt.subplot(ntwk.nports, ntwk.nports, i * ntwk.nports + j + 1)
                    ntwk.plot_s_db(m=i, n=j, label=f'Original S{i+1}{j+1}')
                    s_fit = vf.get_model_response(i=i, j=j, freqs=freq)
                    plt.plot(freq, 20 * np.log10(np.abs(s_fit)), label=f'Fitted S{i+1}{j+1}')
                    plt.xlabel('Frequency (GHz)')
                    plt.ylabel('Magnitude (dB)')
                    plt.legend()
                    plt.grid(True)
            plt.tight_layout()
            plt.show()

    except Exception as e:
        logger.error(f"Ошибка при выполнении векторной аппроксимации: {e}")
