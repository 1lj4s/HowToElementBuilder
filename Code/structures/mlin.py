import numpy as np
import os
import logging
from scipy.interpolate import interp1d
from Code.core.base_structure import BaseStructure
from Code.config import FILES_DIR

RESET = "\033[0m"
GREEN = "\033[32m"
class InfoColorFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        if record.levelname == "INFO":
            return f"{GREEN}{message}{RESET}"
        return message

logging.basicConfig(level=logging.INFO, format=f'{GREEN}%(asctime)s - %(levelname)s - %(message)s{RESET}')
handler = logging.getLogger().handlers[0]
handler.setFormatter(InfoColorFormatter("%(asctime)s %(levelname)s: %(message)s"))
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