#SIM:
L = length
DW = 5*W
DL = DW
sub_w = W / 10
sub_s = W / 10
sub_d = DW / 10
sub_t = T / 3
sub_l = L / 10

SET_INFINITE_GROUND3D(1)

DIELS = {"er0": ER0, "td0": TD0, "er1": ER0, "td1": TD0}
CONDS = []
CONDS.append(COND3D(DW, W, H, T, DL, L, DIELS, sub_w, sub_t, sub_l, type=True, pos=True))
conf0 = GET_CONFIGURATION_3D()

DIELS = {"er0": ER1, "td0": TD1, "er1": ER0, "td1": TD0}
CONDS = []
CONDS.append(COND3D(DW, W, H, T, DL, L, DIELS, sub_w, sub_t, sub_l, type=True, pos=True))
DIEL3D(H, T, DIELS, CONDS, sub_w, sub_l, sub_d)
conf = GET_CONFIGURATION_3D()

result = CalMat(conf, conf0, f0, L, loss=loss)
ECHO()
ECHO(json.dumps(result))