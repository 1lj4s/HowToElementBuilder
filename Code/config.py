import numpy as np

SIMULATIONS = {
    "SPARAM":
        {
            "f0": [0.8e9, 1.e9, 5.e9, 10.e9, 50.e9], # np.linspace(1.5e9, 3.5e9, 2)
            "freq_range": np.linspace(0.1e9, 67.e9, 100),
            "loss": True,
            "sigma": None,
            "seg_cond": 3.0,
            "seg_diel": 1.0,
            "do_vector_fitting": False,
        }
}
SUBSTRATES = {
    "MSUB":
        {
            "T": 2e-6,
            "H": 100.e-6,
            "ER0": 1.0,
            "MU0": 1.0,
            "TD0": 0.0,
            "ER1": 12.9,
            "MU1": 1.0001,
            "TD1": 0.003,
        },
    "M2SUB":
        {
            "T": 2e-6,
            "T2": 2e-6,
            "H1": 100.e-6,
            "H2": 20.e-6,
            "ER0": 1.0,
            "MU0": 1.0,
            "TD0": 0.0,
            "ER1": 12.9,
            "MU1": 1.0001,
            "TD1": 0.003,
            "ER2": 3.,
            "MU2": 1.0002,
            "TD2": 0.003,
        }
}
STRUCTURES = {
    "M1LIN_STRUCTS": ["MLIN", "MLSC", "MLEF", "MTRACE2", "MCURVE"],
    "MNLIN_STRUCTS": ["MCLIN", "MCFIL", "MXCLIN"],
    "MLIN": # однопроводная лп
        {
            "W": 70e-6,
            "length": 500.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MTRACE2":  # однопроводная лп, с автотрассировкой (M1LIN_STRUCTS)
        {
            "W": 70e-6,
            "length": 500.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MLSC": # однопроводная лп, земля на дальнем конце
        {
            "W": 70.e-6,
            "length": 500.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MLEF": # однопроводная лп, обрыв на дальнем конце
        {
            "W": 70.e-6,
            "length": 500.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",
            "SIMULATION": "SPARAM",
        },
    "MTAPER": # N однопроводных лп шириной от W1 до W2, каждая длиной L/N
        {
            "W1": 70.e-6,
            "W2": 170.e-6,
            "length": 500.e-6,
            "Taper": "Linear",  # Linear or Exponential sweep of W
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
            "N": 5, #кол-во точек до интерполяции
            "N2": 100 #кол-во точек после интерполяции
        },
    "MRSTUB2W": # Множество однопроводных лп шириной от W до
        {
            "W": 70.e-6, # Начальная ширина
            "Ro": 250.e-6, # Длина
            "Theta": 20, # Угол
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
            "Taper": "Linear",  # Linear or Exponential sweep of W
            "N": 5,  # кол-во точек до интерполяции
            "N2": 100  # кол-во точек после интерполяции
        },
    "MCLIN": # Двухпроводная ЛП
        {
            "W": [70e-6, 80e-6],
            "W2": 70e-6,
            "S": [30e-6],
            "length": 500.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MCFIL": # Двухпроводная ЛП, первый проводник в обрыве на дальнем конце, второй на ближнем
        {
            "W": [70e-6, 80e-6],
            "W2": 70.e-6,
            "S": [30e-6],
            "length": 500.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",
            "SIMULATION": "SPARAM",
        },
    "MXCLIN":  # X-проводная ЛП (MNLIN_STRUCTS)
        {
            "W": [50e-6, 60e-6, 70e-6, 80e-6],
            "S": [50e-6, 60e-6, 70e-6],
            "N": 5, # Число проводников (в будущем: дает ввести столько W и S сколько надо)
            "length": 500.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",
            "SIMULATION": "SPARAM",
        },
    "MBEND":
        {
            "W1": 70.e-6,
            "W2": 70.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MCURVE":
        {
            "W": 70.e-6,
            "Angle": 90,
            "R": 150.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  #2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MTEE":
        {
            "W1": 70.e-6,
            "W2": 70.e-6,
            "W3": 70.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog", # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MCROSS":
        {
            "W1": 70.e-6,
            "W2": 70.e-6,
            "W3": 70.e-6,
            "W4": 70.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MXOVER": # Пересечение линий передачи на разных слоях
        {
            "W": 70.e-6,
            "W1": 70.e-6,
            "W2": 70.e-6,
            "length": 70.e-6,
            "SUBSTRATE": "M2SUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MGAPX": # Разрыв меду ЛП
        {
            "W": 70.e-6,
            "S": 20.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MSTEP": # Ступенчато-импедансный переход. sub не работает C<0,
        {
            "W1": 50.e-6,
            "W2": 70.e-6,
            "NumPorts": 2,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MOPEN": # Иммитация краевого эффекта на конце лп
        {
            "W": 70.e-6,
            "NumPorts": 1,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        },
    "MLANG": # Две n-проводные линии, которые надо правильно соединить
        {
            "N": 4,
            "W": 40.e-6,
            "S": 40.e-6,
            "L": 100.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic
            "SIMULATION": "SPARAM",
        }
}
