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