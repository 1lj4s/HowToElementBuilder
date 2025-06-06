from Code.config import AVAILABLE_STRUCTURES, AVAILABLE_SIMULATIONS, JSON_PATH, create_default_config
from Code.structures.mlin import MLIN
from Code.structures.mtaper import MTAPER
from Code.structures.mxover import MXOVER
from Code.structures.mclin import MCLIN
from Code.structures.tfr import TFR
from Code.structures.mopen import MOPEN
from Code.structures.mstep import MSTEP
from Code.structures.mlef import MLEF
from Code.structures.mbend90x import MBEND90X
from Code.simulations.sym_sub_test import SymSubTest
from Code.simulations.sym_snp_test import SymSnpTest
from Code.symica.sym_spice import run_symspice
from Code.input.input import SimulationConfigBuilder

def main():

    structure_name = "MBEND90X"  # "MLIN", "MLEF", "MCLIN", "MTAPER", "MXOVER", "MBEND90X", "MSTEP", "MOPEN", "TFR"
    simulation_type = "sym_snp_test" # "sym_sub_test", "sym_snp_test", "CustomCir"
    current_run = "test"

    # Создание конфигурации
    create_default_config()

    # Выбор структуры
    if structure_name == "MLIN":
        structure = MLIN(structure_name, JSON_PATH)
    elif structure_name == "MLEF":
        structure = MLEF(structure_name, JSON_PATH)
    elif structure_name == "MCLIN":
        structure = MCLIN(structure_name, JSON_PATH)
    elif structure_name == "MTAPER":
        structure = MTAPER(structure_name, JSON_PATH)
    elif structure_name == "MXOVER":
        structure = MXOVER(structure_name, JSON_PATH)
    elif structure_name == "MBEND90X":
        structure = MBEND90X(structure_name, JSON_PATH)
    elif structure_name == "TFR":
        structure = TFR(structure_name, JSON_PATH)
    elif structure_name == "MOPEN":
        structure = MOPEN(structure_name, JSON_PATH)
    elif structure_name == "MSTEP":
        structure = MSTEP(structure_name, JSON_PATH)
    else:
        raise ValueError(f"Структура {structure_name} не поддерживается. Доступные структуры: {AVAILABLE_STRUCTURES}")

    # Получение пути к .cir файлу из конфигурации
    config_builder = SimulationConfigBuilder(JSON_PATH)
    structure_config = config_builder.get_structure(structure_name)
    input_cir_file = structure_config.get("result_path", None)
    if simulation_type == "CustomCir" and not input_cir_file:
        raise ValueError(f"Для CustomCir требуется указать путь к .cir файлу в конфигурации {structure_name}")

    # Выбор симуляции
    if simulation_type == "sym_sub_test":
        simulation = SymSubTest(structure, current_run)
        simulation.run()
    elif simulation_type == "sym_snp_test":
        simulation = SymSnpTest(structure, current_run)
        simulation.run()
    elif simulation_type == "CustomCir":
        run_symspice(
            scs_file="CustomCir",
            obj_file=input_cir_file,
            structure_name=structure_name,
            num_ports=structure.num_ports
        )
    else:
        raise ValueError(f"Тип симуляции {simulation_type} не поддерживается. Доступные симуляции: {AVAILABLE_SIMULATIONS}")

if __name__ == "__main__":
    main()