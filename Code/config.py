import numpy as np

SIMULATIONS = {
    "SPARAM": [
        {
            "f0": [0.1e9, 0.5e9, 1.e9, 5.e9, 10.e9, 50.e9],
            "freq_range": np.linspace(0.1e9, 67e9, 100),
            "loss": True,
            "sigma": None,
            "seg_cond": 3.0,
            "seg_diel": 1.0,
            "do_vector_fitting": True,
        }
    ],
}
SUBSTRATES = {
    "MSUB": [
        {
            "T": 2e-6,
            "H": 100.e-6,
            "ER0": 1.0,
            "MU0": 1.0,
            "TD0": 0.0,
            "ER1": 12.9,
            "MU1": 1.0001,
            "TD1": 0.003,
        }
    ],
    "M2SUB": [
        {
            "T": 2e-6,
            "T2": 2e-6,
            "H1": 100.e-6,
            "H2": 100.e-6,
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
    ],
}
STRUCTURES = {
    "M1LIN": [
        {
            "W": 10e-6,
            "length": 0.1,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "M2LIN": [
        {
            "W1": 10e-6,
            "W2": 15e-6,
            "S": 10e-6,
            "length": 0.1,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MNLIN": [
        {
            "W": [10.e-6, 10.e-6, 10.e-6, 10.e-6, 10.e-6],
            "S": [10.e-6, 10.e-6, 10.e-6, 10.e-6],
            "length": 0.1,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic
            "SIMULATION": "SPARAM",
        }
    ],
    "MTEE": [
        {
            "W1": 10.e-6,
            "W2": 15.e-6,
            "W3": 20.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog", # Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "TFR": [
        {
            "W": 10.e-6,
            "L": 15.e-6,
            "RS": 50,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog", # Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MSTEP": [
        {
            "W1": 10.e-6,
            "W2": 15.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MLEF": [
        {
            "W": 10.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Talgat",
            "SIMULATION": "SPARAM",
        }
    ],
    "MOPEN": [
        {
            "W": 10.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MCURVE": [
        {
            "W": 10.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MBEND": [
        {
            "W1": 10.e-6,
            "W2": 15.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MCFIL": [
        {
            "W1": 10.e-6,
            "W2": 15.e-6,
            "S": 15.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",
            "SIMULATION": "SPARAM",
        }
    ],
    "MCROSS": [
        {
            "W1": 10.e-6,
            "W2": 15.e-6,
            "W3": 20.e-6,
            "W4": 25.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MSTUB2W": [
        {
            "W": 10.e-6,
            "Ro": 15.e-6,
            "Theta": 20.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "Verilog",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MXOVER": [
        {
            "W1": 10.e-6,
            "W2": 10.e-6,
            "SUBSTRATE": "MSUB2",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MGAPX": [
        {
            "W1": 10.e-6,
            "W2": 10.e-6,
            "S": 10.e-6,
            "SUBSTRATE": "MSUB1",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MTAPER": [
        {
            "W1": 10.e-6,
            "W2": 50.e-6,
            "L": 100.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MLSC": [
        {
            "W": 10.e-6,
            "L": 100.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic or Verilog or Subcircuit
            "SIMULATION": "SPARAM",
        }
    ],
    "MLANG": [
        {
            "W": 40.e-6,
            "S": 40.e-6,
            "L": 100.e-6,
            "SUBSTRATE": "MSUB",
            "MODELTYPE": "2D_Quasistatic",  # 2D_Quasistatic
            "SIMULATION": "SPARAM",
        }
    ],
}
