from Code.config import AVAILABLE_STRUCTURES, AVAILABLE_SIMULATIONS, JSON_PATH, create_default_config
from Code.structures.mlin import MLIN
from Code.structures.mtaper import MTAPER
from Code.structures.mxover import MXOVER
from Code.simulations.sym_sub_test import SymSubTest
from Code.simulations.sym_snp_test import SymSnpTest
from database.postgres import plot_comparison as plot_results
import os

def main():
    structure_name = "MLIN"  # # MCLIN, MLEF, MXOVER, MSTEP, MBEND90X, MOPENX, MTEE, MTAPER
    simulation_type = "sym_snp_test"  # "sym_snp_test" или "sym_sub_test"
    current_run = "test"

    # Создание конфигурации
    builder = create_default_config()

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
    W = builder.get_structure(structure_name)["W1"]
    L = builder.get_structure(structure_name)["length"]
    base_dir = os.path.abspath(os.path.dirname(__file__))
    output_file = os.path.join(base_dir,"Files", "sym", f"{structure_name}_{current_run}.s2p")
    print(f"{structure_name}_{W*1e6}_{L*1e6}_.s2p")
    if structure_name == "MLIN":
        plot_results(f"{structure_name}_{W*1e6}_{L*1e6}_.s2p",output_file)
    elif structure_name == "MTAPER":
        W2 = builder.get_structure(structure_name)["W2"]
        plot_results(f"{structure_name}_{W * 1e6}__{W2 * 1e6}_{L * 1e6}_.s2p", output_file)


if __name__ == "__main__":
    main()