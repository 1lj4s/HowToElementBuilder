register_talgat_commands()
INCLUDE("UTIL")
INCLUDE("MATRIX")
INCLUDE("MOM3D")
import numpy as np
from numpy import array, arange, sqrt, linspace
import json
import os


def COND3D(x0, x, y0, y, z0, z, diels, segx, segy, segz, type=True, pos=True):
    if type:
        CONDUCTOR3D()
    else:
        CONDUCTOR3D_GROUNDED()
    if pos:
        y0 = y0
        ERmid = diels['er0']
        TDmid = diels['td0']
    else:
        y0 = y0 - y
        ERmid = diels['er1']
        TDmid = diels['td1']

    SET_ER_PLUS3D(diels['er0'])
    SET_TAN_DELTA_PLUS3D(diels['td0'])
    SET_SUBINTERVALS_X(round(x / segx))
    SET_SUBINTERVALS_Y(round(z / segz))
    RECT_XZ(y0 + y, x0, z0, x0 + x, z0 + z)
    SET_ER_PLUS3D(ERmid)
    SET_TAN_DELTA_PLUS3D(TDmid)
    SET_SUBINTERVALS_X(round(x / segx))
    SET_SUBINTERVALS_Y(round(y / segy))
    RECT_XY(z0 + z, x0, y0, x0 + x, y0 + y)
    RECT_XY(z0, x0, y0, x0 + x, y0 + y)
    SET_SUBINTERVALS_X(round(z / segz))
    SET_SUBINTERVALS_Y(round(y / segy))
    RECT_ZY(x0, z0, y0, z0 + z, y0 + y)
    RECT_ZY(x0 + x, z0, y0, z0 + z, y0 + y)
    SET_ER_PLUS3D(diels['er1'])
    SET_TAN_DELTA_PLUS3D(diels['td1'])
    SET_SUBINTERVALS_X(round(x / segx))
    SET_SUBINTERVALS_Y(round(z / segz))
    RECT_XZ(y0, x0, z0, x0 + x, z0 + z)

    return {"x0": x0, "x": x, "z0": z0, "z": z, "segx": segx, "segz": segz}

def DIEL3D(h, diels, conds, segs, segw, segl, segd):

    DIELECTRIC3D()
    SET_ER_PLUS3D(diels['er0'])
    SET_TAN_DELTA_PLUS3D(diels['td0'])
    SET_ER_MINUS3D(diels['er1'])
    SET_TAN_DELTA_MINUS3D(diels['td1'])
    """pdd"""
    SET_SUBINTERVALS_X(round(conds[0]['x0'] / segd))
    SET_SUBINTERVALS_Y(round(conds[0]['z0'] / segd))
    RECT_XZ(h, 0, 0, conds[0]['x0'], conds[0]['z0'])
    RECT_XZ(h, 0, conds[0]['z0'] + conds[0]['z'], conds[0]['x0'], 2 * conds[0]['z0'] + conds[0]['z'])
    RECT_XZ(h, conds[-1]['x0'] + conds[-1]['x'], 0, conds[0]['x0'] + conds[-1]['x0'] + conds[-1]['x'], conds[0]['z0'])
    RECT_XZ(h, conds[-1]['x0'] + conds[-1]['x'], conds[0]['z0'] + conds[0]['z'],
            conds[0]['x0'] + conds[-1]['x0'] + conds[-1]['x'], 2 * conds[0]['z0'] + conds[0]['z'])
    """pdl"""
    SET_SUBINTERVALS_X(round(conds[0]['x0'] / segd))
    SET_SUBINTERVALS_Y(round(conds[0]['z'] / segl))
    RECT_XZ(h, 0, conds[0]['z0'], conds[0]['x0'], conds[0]['z0'] + conds[0]['z'])
    RECT_XZ(h, conds[-1]['x0'] + conds[-1]['x'], conds[0]['z0'], conds[0]['x0'] + conds[-1]['x0'] + conds[-1]['x'],
            conds[0]['z0'] + conds[0]['z'])
    """pwd"""
    SET_SUBINTERVALS_X(round(conds[-1]['x'] / segw))
    SET_SUBINTERVALS_Y(round(conds[0]['z0'] / segd))
    RECT_XZ(h, conds[-1]['x0'], 0, conds[-1]['x0'] + conds[-1]['x'], conds[0]['z0'])
    RECT_XZ(h, conds[-1]['x0'], conds[0]['z0'] + conds[0]['z'], conds[-1]['x0'] + conds[-1]['x'],
            2 * conds[0]['z0'] + conds[0]['z'])

    for i in range(len(conds) - 1):
        """psd"""
        SET_SUBINTERVALS_X(round((conds[i + 1]['x0'] - (conds[i]['x0'] + conds[i]['x'])) / segs))
        SET_SUBINTERVALS_Y(round(conds[0]['z0'] / segd))
        RECT_XZ(h, conds[i]['x0'] + conds[i]['x'], 0, conds[i + 1]['x0'], conds[0]['z0'])
        RECT_XZ(h, conds[i]['x0'] + conds[i]['x'], conds[0]['z0'] + conds[0]['z'], conds[i + 1]['x0'],
                2 * conds[0]['z0'] + conds[0]['z'])
        """psl"""
        SET_SUBINTERVALS_X(round((conds[i + 1]['x0'] - (conds[i]['x0'] + conds[i]['x'])) / segs))
        SET_SUBINTERVALS_Y(round(conds[0]['z'] / segl))
        RECT_XZ(h, conds[i]['x0'] + conds[i]['x'], conds[0]['z0'], conds[i + 1]['x0'], conds[0]['z0'] + conds[0]['z'])
        """pwd"""
        SET_SUBINTERVALS_X(round(conds[i]['x'] / segw))
        SET_SUBINTERVALS_Y(round(conds[0]['z0'] / segd))
        RECT_XZ(h, conds[i]['x0'], 0, conds[i]['x0'] + conds[i]['x'], conds[0]['z0'])
        RECT_XZ(h, conds[i]['x0'], conds[0]['z0'] + conds[0]['z'], conds[i]['x0'] + conds[i]['x'],
                2 * conds[0]['z0'] + conds[0]['z'])

def CalMat(conf, conf0, f0, L, loss=False):
    mC0 = CALCULATE_C3D(SMN_C3D(conf0), conf0)
    mC = CALCULATE_C3D(SMN_C3D(conf), conf)
    n = GET_MATRIX_ROWS(mC0)
    if loss:
        smn_CG3D = SMN_CG3D(conf)
        mR_arr = np.zeros((n, n, len(f0)))
        mG_arr = np.zeros((n, n, len(f0)))
        for idx in range(len(f0)):
            freq = f0[idx]
            mCG3D = CALCULATE_CG3D(smn_CG3D, conf, freq)
            # mG3D = GET_IMAG_MATRIX(cg3d)
            for i in range(n):
                for j in range(n):
                    mG_arr[i, j, idx] = np.imag(GET_MATRIX_VALUE(mCG3D, i, j)) / L
    else:
        mR_arr = np.zeros((n, n, 1)) / L
        mG_arr = np.zeros((n, n, 1)) / L

    mL_arr = calcL(t2n(mC0), L) / L
    mC_arr = t2n(mC) / L

    return {
        'mL': mL_arr.tolist(),
        'mC': mC_arr.tolist(),
        'mR': mR_arr.tolist(),
        'mG': mG_arr.tolist()
    }

def calcL(mC0, L):
    c = 3.e8
    mu = 4 * np.pi * 1e-7
    epsilon = 1 / (mu * c ** 2)
    return mu * epsilon * np.linalg.inv(mC0 / L) * L

def t2n(talmat):
    n = GET_MATRIX_ROWS(talmat)
    npmat = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            npmat[i, j] = GET_MATRIX_VALUE(talmat, i, j)
    return npmat