import numpy as np

CONFIG = {
    "M1LIN": [
        {
            "W": 10e-6,
            "S": 10e-6,
            "T": 2e-6,
            "f0": [0.1e9, 0.5e9, 1.e9, 5.e9, 10.e9, 50.e9],
            "freq_range": np.linspace(0.1e9, 67e9, 100),
            "Z0": 50,
            "length": 0.1,
            "loss": True,
            "sigma": None,
            "H": 100.e-6,
            "ER0": 1.0,
            "ER1": 12.9,
            "MU0": 1.0,
            "MU1": 1.0001,
            "TD0": 0.0,
            "TD1": 0.003,
            "seg_cond": 3.0,
            "seg_diel": 1.0,
            "do_vector_fitting": True
        }
    ],
    "M2LIN": [
        {
            "W1": 10e-6,
            "W2": 15e-6,
            "S": 10e-6,
            "T": 2e-6,
            "f0": [0.1e9, 0.5e9, 1.e9, 5.e9, 10.e9, 50.e9],
            "freq_range": np.linspace(0.1e9, 67e9, 100),
            "Z0": 50,
            "length": 0.1,
            "loss": True,
            "sigma": None,
            "H": 100.e-6,
            "ER0": 1.0,
            "ER1": 12.9,
            "MU0": 1.0,
            "MU1": 1.0001,
            "TD0": 0.0,
            "TD1": 0.003,
            "seg_cond": 3.0,
            "seg_diel": 1.0,
            "do_vector_fitting": True
        }
    ],
    "MNLIN": [
        {
            "W": [10.e-6, 10.e-6, 10.e-6, 10.e-6, 10.e-6],
            "S": [10.e-6, 10.e-6, 10.e-6, 10.e-6],
            "T": 2e-6,
            "f0": [0.01e9, 0.05e9, 0.1e9, 0.5e9, 1.e9, 5.e9, 10.e9, 50.e9],
            "freq_range": np.linspace(0.1e9, 67e9, 100),
            "Z0": 50,
            "length": 0.1,
            "loss": True,
            "sigma": None,
            "H": 100.e-6,
            "ER0": 1.0,
            "ER1": 12.9,
            "MU0": 1.0,
            "MU1": 1.0001,
            "TD0": 0.0,
            "TD1": 0.003,
            "seg_cond": 3.0,
            "seg_diel": 1.0,
            "do_vector_fitting": True
        }
    ]
}
