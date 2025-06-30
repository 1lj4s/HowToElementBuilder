#SIM:
DW = 5*W[0]
DL = DW
sub_w = W[0] / 5
sub_s = S[0] / 3
sub_d = W[0] / 2
sub_t = T / 3
sub_l = W[0] / 5

SET_INFINITE_GROUND3D(1)

DIELS = {"er0": ER0, "td0": TD0, "er1": ER0, "td1": TD0}
CONDS = []
for i in range(len(W)-1):
    CONDS.append(COND3D(DW, W[i], H, T, W[0], L, DIELS, sub_w, sub_t, sub_l, type=True, pos=True))
    DW = DW + S[i] + W[i]
CONDS.append(COND3D(DW, W[-1], H, T, W[0], L, DIELS, sub_w, sub_t, sub_l, type=True, pos=True))
conf0 = GET_CONFIGURATION_3D()
# DRAW_CONFIGURATION3D(conf0)

DW = 5*W[0]
DIELS = {"er0": ER1, "td0": TD1, "er1": ER0, "td1": TD0}
CONDS = []
for i in range(len(W)-1):
    CONDS.append(COND3D(DW, W[i], H, T, W[0], L, DIELS, sub_w, sub_t, sub_l, type=True, pos=True))
    DW = DW + S[i] + W[i]
CONDS.append(COND3D(DW, W[-1], H, T, W[0], L, DIELS, sub_w, sub_t, sub_l, type=True, pos=True))
DIEL3D(H, DIELS, CONDS, sub_w, sub_l, sub_d, sub_s)
conf = GET_CONFIGURATION_3D()
# DRAW_CONFIGURATION3D(conf)

result = CalMat(conf, conf0, f0, L, loss=loss)
ECHO()
ECHO(json.dumps(result))