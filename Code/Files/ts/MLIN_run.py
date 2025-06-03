
register_talgat_commands()
INCLUDE("UTIL")
INCLUDE("RESPONSE")
INCLUDE("MATRIX")
INCLUDE("MOM2D")
INCLUDE("TLX")
INCLUDE("INFIX")
INCLUDE("GRAPH")
import numpy as np
import os


def cond(X, Y, W, T, D1, D2, TOP, GND):
    if TOP:
        c = 1.
        a = 0.
        na = 1.
    else:
        c = -1.
        a = 1.
        na = 0.
    if GND:
        CONDUCTOR_GROUNDED()
    else:
        CONDUCTOR()
    SET_ER_PLUS(D1[0])
    SET_MU_PLUS(D1[1])
    SET_TAN_DELTA_PLUS(D1[2])
    LINE(X + a * W, Y, X + na * W, Y)
    SET_ER_PLUS(D2[0])
    SET_MU_PLUS(D2[1])
    SET_TAN_DELTA_PLUS(D2[2])
    LINETO(X + na * W, Y + c * T)
    LINETO(X + a * W, Y + c * T)
    LINETO(X + a * W, Y)
    return [X, W]


def diel1(A, H, D1, D0):
    N = len(A)
    DIELECTRIC()
    SET_ER_PLUS(D1[0])
    SET_MU_PLUS(D1[1])
    SET_TAN_DELTA_PLUS(D1[2])
    SET_ER_MINUS(D0[0])
    SET_MU_MINUS(D0[1])
    SET_TAN_DELTA_MINUS(D0[2])
    LINE(0, H, A[0][0], H)
    LINE(A[N-1][0] + A[N-1][1], H, A[N-1][0] + A[N-1][1] + A[0][0], H)
    if N >= 2:
        for i1 in range(N-1):
            LINE(A[i1][0] + A[i1][1], H, A[i1+1][0], H)


def CalMat(conf, f0, loss=False, sigma=None):
    smn_L = SMN_L_OMP(conf)
    mL = CALCULATE_L(smn_L, conf)
    if loss:
        smn_CG = SMN_CG_OMP(conf)
        mC = CALCULATE_C(SMN_C_OMP(conf), conf)
        n = GET_MATRIX_ROWS(mL)
        mR_arr = np.zeros((n, n, len(f0)))
        mG_arr = np.zeros((n, n, len(f0)))
        for idx in range(len(f0)):
            freq = f0[idx]
            mR = CALCULATE_R(smn_L, conf, freq, sigma)
            cg = CALCULATE_CG(smn_CG, conf, freq)
            mG = GET_IMAG_MATRIX(cg)
            for i in range(n):
                for j in range(n):
                    mR_arr[i, j, idx] = GET_MATRIX_VALUE(mR, i, j)
                    mG_arr[i, j, idx] = GET_MATRIX_VALUE(mG, i, j)
    else:
        mC = CALCULATE_C(SMN_C_OMP(conf), conf)
        n = GET_MATRIX_ROWS(mL)
        mR_arr = np.zeros((n, n, 1))
        mG_arr = np.zeros((n, n, 1))
    mL_arr = np.zeros((n, n))
    mC_arr = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            mL_arr[i, j] = GET_MATRIX_VALUE(mL, i, j)
            mC_arr[i, j] = GET_MATRIX_VALUE(mC, i, j)
    return {
        'mL': mL_arr,
        'mC': mC_arr,
        'mR': mR_arr,
        'mG': mG_arr
    }


def SaveRes(path, data_dict):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    if not path.endswith(".npy"):
        path += ".npy"
    np.save(path, data_dict)
    print(f"[!] Result saved to: {path}")


W = 1e-05
result_path = r'D:\saves\Pycharm\HowToElementBuilder\Code\Files\npy\MLIN_test_10.npy'
params = {'result_path': 'D:\\saves\\Pycharm\\HowToElementBuilder\\Code\\Files\\npy\\MLIN_test.npy', 'f0': [100000000.0, 500000000.0, 1000000000.0, 5000000000.0, 10000000000.0, 20000000000.0, 30000000000.0, 40000000000.0], 'seg_cond': 3.0, 'seg_diel': 1.0, 'loss': True, 'sigma': None, 'ER0': 1.0, 'MU0': 1.0, 'TD0': 0.0, 'ER1': 9.7, 'MU1': 1.0001, 'TD1': 0.003, 'T': 5.1e-06, 'H': 0.0001, 'W1': 1e-05, 'length': 0.01, 'Z0': 50, 'num_ports': 2}
f0 = params["f0"]
seg_cond = params["seg_cond"]
seg_diel = params["seg_diel"]
loss = params["loss"]
sigma = params["sigma"]
ER0 = params["ER0"]
MU0 = params["MU0"]
TD0 = params["TD0"]
ER1 = params["ER1"]
MU1 = params["MU1"]
TD1 = params["TD1"]
T = params["T"]
H = params["H"]
D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
CC1.append(cond(2 * W, H, W, T, D1, D0, True, False))
diel1(CC1, H, D1, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
SaveRes(result_path, result)
