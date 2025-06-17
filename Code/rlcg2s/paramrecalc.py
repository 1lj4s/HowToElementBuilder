import numpy as np

def mrstubparamrecalc(mrstub):
    W1 = mrstub['W']
    length = mrstub['Ro']
    Theta = mrstub['Theta']
    length1 = 180 * W1 / (np.pi * Theta)
    length2 = length - length1
    W2 = length * np.pi * Theta / 180
    return W1, W2, length2

def mcurveparamrecalc(mcurve):
    W = mcurve['W']
    Angle = mcurve['Angle']
    R = mcurve['R']
    length = R * Angle * np.pi / 180
    return length

if __name__ == "__main__":
    STRUCTURES = {
        "MRSTUB2W": # Множество однопроводных лп шириной от W до
            {
                "W": 70.e-6, # Начальная ширина
                "Ro": 250.e-6, # Длина
                "Theta": 45, # Угол
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
                "MODELTYPE": "Verilog",  # Verilog or Subcircuit
                "SIMULATION": "SPARAM",
            },
        }
    W1, W2, length = mrstubparamrecalc(STRUCTURES['MRSTUB2W'])
    length = mcurveparamrecalc(STRUCTURES['MCURVE'])