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