import numpy as np

SIMULATIONS = {
    "SPARAM":
        {
            "f0": [0.1e9, 0.25e9, 0.5e9, 1.e9, 2.5e9, 5.e9, 10.e9, 25.e9, 50.e9], # np.linspace(1.5e9, 3.5e9, 2) [0.8e9, 1.e9, 5.e9, 10.e9, 50.e9]
            "freq_range": np.linspace(0.1e9, 67.e9, 335),
            "loss": True,
            "sigma": None,
            "seg_cond": 1.0,
            "seg_diel": 1.0,
            "do_vector_fitting": False,
        }
}
SUBSTRATES = {
    "SUB1":
        {
            "T": 2.e-6,
            "H": 100.e-6,
            "ER0": 1.0,
            "MU0": 1.0,
            "TD0": 0.0,
            "ER1": 12.9,
            "MU1": 1.0001,
            "TD1": 0.003,
        },
    "SUB2":
        {
            "T": 35.e-6,
            "H": 1000.e-6,
            "ER0": 1.0,
            "MU0": 1.0,
            "TD0": 0.0,
            "ER1": 3.5,
            "MU1": 1.0001,
            "TD1": 0.003,
        },
    "M2SUB1":
        {
            "T": 2.e-6,
            "T2": 2.e-6,
            "H1": 100.e-6,
            "H2": 2.25e-6,
            "ER0": 1.0,
            "MU0": 1.0,
            "TD0": 0.0,
            "ER1": 12.9,
            "MU1": 1.0001,
            "TD1": 0.003,
            "ER2": 3.,
            "MU2": 1.0002,
            "TD2": 0.001,
        },
    "M2SUB2":
        {
            "T": 35.e-6,
            "T2": 35.e-6,
            "H1": 225.e-6,
            "H2": 1000.e-6,
            "ER0": 1.0,
            "MU0": 1.0,
            "TD0": 0.0,
            "ER1": 2.1,
            "MU1": 1.0001,
            "TD1": 0.001,
            "ER2": 4.5,
            "MU2": 1.0002,
            "TD2": 0.003,
        }
}
STRUCTURES = {
    "M1LIN_STRUCTS": ["MLIN", "MLSC", "MLEF", "MTRACE2", "MCURVE"],
    "MNLIN_STRUCTS": ["MCLIN", "MCFIL", "MXCLIN"],
    "MLIN": # однопроводная лп
        {
            "W": 195.e-6,
            "length": 3500.e-6,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
    "MTRACE2":  # однопроводная лп, с автотрассировкой (M1LIN_STRUCTS)
        {
            "W": 100e-6,
            "length": 500.e-6,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "3D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
    "MLSC":  # однопроводная лп, земля на дальнем конце
        {
            "W": 195.e-6,
            "length": 3500.e-6,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "3D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
    "MLEF":  # однопроводная лп, обрыв на дальнем конце
        {
            "W": 195.e-6,
            "length": 3500.e-6,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
    "MTAPER": # N однопроводных лп шириной от W1 до W2, каждая длиной L/N
        {
            "W1": 30.e-6,
            "W2": 195.e-6,
            "length": 3500.e-6,
            "Taper": "Linear",  # Linear or Exponential sweep of W
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "3D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic
            "SIMULATION": "SPARAM",
            "N": 5, #кол-во точек до интерполяции
            "N2": 100 #кол-во точек после интерполяции
        },
    "MRSTUB2W": # Множество однопроводных лп шириной от W до
        {
            "W": 30.e-6, # Начальная ширина
            "Ro": 195.e-6, # Длина
            "Theta": 45, # Угол
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "3D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
            "Taper": "Linear",  # Linear or Exponential sweep of W
            "N": 5,  # кол-во точек до интерполяции
            "N2": 100  # кол-во точек после интерполяции
        },
    "MCLIN": # Двухпроводная ЛП
        {
            "W": [195.e-6, 195.e-6],
            "W2": 195.e-6,
            "S": [20.e-6],
            "length": 3500.e-6,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "3D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
    "MCFIL": # Двухпроводная ЛП, первый проводник в обрыве на дальнем конце, второй на ближнем
        {
            "W": [195.e-6, 195.e-6],
            "W2": 195.e-6,
            "S": [20.e-6],
            "length": 3500.e-6,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "3D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
    "MXCLIN":  # X-проводная ЛП (MNLIN_STRUCTS)
        {
            "W": [30.e-6, 75.e-6, 195.e-6],
            "S": [50.e-6, 50.e-6],
            "N": 3, # Число проводников (в будущем: дает ввести столько W и S сколько надо)
            "length": 3500.e-6,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "3D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
    "MBEND":
        {
            "W1": 195.e-6,
            "W2": 195.e-6,
            "NumPorts": 2,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "Verilog",  # Verilog
            "SIMULATION": "SPARAM",
        },
    "MCURVE":
        {
            "W": 10.e-6,
            "Angle": 120,
            "R": 100.e-6,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "3D_Quasistatic",  #2D_Quasistatic or 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
    "MTEE": #*
        {
            "W1": 70.e-6,
            "W2": 70.e-6,
            "W3": 70.e-6,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "2D_Quasistatic", # 2D_Quasistatic or 3D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MCROSS": #*
        {
            "W1": 70.e-6,
            "W2": 70.e-6,
            "W3": 70.e-6,
            "W4": 70.e-6,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MXOVER": # Пересечение линий передачи на разных слоях
        {
            "W": 195.e-6,
            "W1": 195.e-6,
            "W2": 195.e-6,
            "length": 195.e-6,
            "SUBSTRATE": "M2SUB1",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or 3D_Quasistatic
            "SIMULATION": "SPARAM",
        },
    "MGAPX": # Разрыв меду ЛП
        {
            "W": 195.e-6,
            "S": 30.e-6,
            "NumPorts": 2,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "Verilog",  # Verilog
            "SIMULATION": "SPARAM",
        },
    "MSTEP": # Ступенчато-импедансный переход. sub не работает C<0,
        {
            "W1": 195.e-6,
            "W2": 30.e-6,
            "NumPorts": 2,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "Subcircuit",  # Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MOPEN": # Иммитация краевого эффекта на конце лп
        {
            "W": 195.e-6,
            "NumPorts": 1,
            "SUBSTRATE": "SUB1",
            "MODELTYPE": "Subcircuit",  # Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
}
elements_for_subst_check = ["MLIN"]
subst_conditions = {
    "SUB1": {
        "ER1": 12.6,
        "H": 100e-6,
        "T": 2e-6,
        "valid_W": [195, 75, 30, 4700, 2200, 1200],  # значения в микрометрах
        "valid_length": [3500, 7500, 15000]          # значения в микрометрах
    },
    "SUB2": {
        "ER1": 3.5,
        "H": 1000e-6,
        "T": 35e-6,
        "valid_W": [195, 75, 30, 4700, 2200, 1200],
        "valid_length": [3500, 7500, 15000]
    }
}