from Code.config import AVAILABLE_STRUCTURES, AVAILABLE_SIMULATIONS, JSON_PATH, create_default_config
from Code.structures.mlin import MLIN
from Code.structures.mtaper import MTAPER
from Code.structures.mxover import MXOVER
from Code.simulations.sym_sub_test import SymSubTest
from Code.simulations.sym_snp_test import SymSnpTest

def main():
    structure_name = "MXOVER"  # "MTAPER" или "MLIN"
    simulation_type = "sym_snp_test"  # "sym_snp_test" или "sym_sub_test"
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