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
        ER2=3.0,  #
        MU2=1.0002,  #
        TD2=0.001,  #
        T=5.1e-6,  #
        H=100.e-6, #
        H1=100.e-6, #
    )
    builder.add_structure(
        struct_name="SIM",
        f0=[0.1e9, 0.5e9, 1.e9, 5.e9, 10.e9, 20.e9, 30.e9, 40.e9], ##
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
        num_ports=2,  ##
    )
    builder.add_structure(
        struct_name="MLEF",
        result_path=os.path.join(FILES_DIR, "npy", "MLIN_test.npy"),
        W1=10.e-6,
        length=0.01,
        num_ports=1,  ##
    )
    builder.add_structure(
        struct_name="MOPEN",
        result_path=os.path.join(FILES_DIR, "npy", "MLIN_test.npy"),
        W1=10.e-6,
        length=0.01,
        num_ports=1,  ##
    )
    builder.add_structure(
        struct_name="MTAPER",
        result_path=os.path.join(FILES_DIR, "npy", "MTAPER_test.npy"),
        W1=10.e-6,
        W2=100.e-6,
        Wtype="lin",
        length=0.01,
        num_ports=2,  ##
    )
    builder.add_structure(
        struct_name="M2LIN",
        result_path=os.path.join(FILES_DIR, "npy", "MLIN_test.npy"),
        W1=10.e-6,
        W2=10.e-6,
        S=10.e-6,
        length=0.01,
        num_ports=4,  ##
    )
    builder.add_structure(
        struct_name="MCFIL",
        result_path=os.path.join(FILES_DIR, "npy", "MLIN_test.npy"),
        W1=10.e-6,
        W2=10.e-6,
        S=10.e-6,
        length=0.01,
        num_ports=2,  ##
    )
    builder.add_structure(
        struct_name="MXOVER",
        result_path=os.path.join(FILES_DIR, "npy", "MLIN_test.npy"),
        W1=10.e-6,
        W2=10.e-6,
        S=10.e-6,
        length=0.01,
        num_ports=4,  ##
    )
    builder.save()