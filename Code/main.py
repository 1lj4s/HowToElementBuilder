from Code.config import AVAILABLE_STRUCTURES, AVAILABLE_SIMULATIONS, JSON_PATH, create_default_config
from Code.structures.mlin import MLIN
from Code.structures.mtaper import MTAPER
from Code.simulations.sym_sub_test import SymSubTest
from Code.simulations.sym_snp_test import SymSnpTest

def main():
    structure_name = "MLIN"  # Или "MLIN"
    simulation_type = "sym_sub_test"  # Или "sym_snp_test"
    current_run = "test"

    # Создание конфигурации (использует SimulationConfigBuilder из input/input.py)
    create_default_config()

    # Выбор структуры
    if structure_name == "MLIN":
        structure = MLIN(structure_name, JSON_PATH)
    elif structure_name == "MTAPER":
        structure = MTAPER(structure_name, JSON_PATH)
    else:
        raise ValueError(f"Структура {structure_name} не поддерживается")

    # Выбор симуляции
    if simulation_type == "sym_sub_test":
        simulation = SymSubTest(structure, current_run)
    elif simulation_type == "sym_snp_test":
        simulation = SymSnpTest(structure, current_run)
    else:
        raise ValueError(f"Тип симуляции {simulation_type} не поддерживается")

    # Запуск симуляции
    simulation.run()

if __name__ == "__main__":
    main()