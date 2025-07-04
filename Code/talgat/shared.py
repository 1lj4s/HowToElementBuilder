register_talgat_commands()
INCLUDE("MATRIX")
INCLUDE("MOM2D")
import json
import numpy as np
import os
from numpy import array

def cond(X, Y, W, T, D1, D2, TOP, GND):
    if TOP:
        c, a, na = 1., 0., 1.
    else:
        c, a, na = -1., 1., 0.
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
    LINE(A[N - 1][0] + A[N - 1][1], H, A[N - 1][0] + A[N - 1][1] + A[0][0], H)
    if N >= 2:
        for i in range(N - 1):
            LINE(A[i][0] + A[i][1], H, A[i + 1][0], H)


def CalMat(conf, f0, loss=False, sigma=None):
    smn_L = SMN_L_OMP(conf)
    mL = CALCULATE_L(smn_L, conf)
    if loss:
        smn_CG = SMN_CG_OMP(conf)
        # mC = CALCULATE_C(SMN_C_OMP(conf), conf)
        n = GET_MATRIX_ROWS(mL)
        mR_arr = np.zeros((n, n, len(f0)))
        mG_arr = np.zeros((n, n, len(f0)))
        for idx in range(len(f0)):
            freq = f0[idx]
            mR = CALCULATE_R(smn_L, conf, freq, sigma)
            cg = CALCULATE_CG(smn_CG, conf, freq)
            mC = GET_REAL_MATRIX(cg)
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
        'mL': mL_arr.tolist(),
        'mC': mC_arr.tolist(),
        'mR': mR_arr.tolist(),
        'mG': mG_arr.tolist()
    }
