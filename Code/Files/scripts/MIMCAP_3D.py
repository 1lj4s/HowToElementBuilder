#SIM:
DW = 5*W
DL = DW
sub_w = W / 5
sub_s = W / 3
sub_d = DW / 3
sub_t1 = T1 / 3
sub_t2 = T2 / 3
sub_l = L / 10

SET_INFINITE_GROUND3D(1)

DIELS = {"er0": ER0, "td0": TD0, "er1": ER0, "td1": TD0}
CONDS = []
CONDS.append(COND3D(DW, W, H1, T1, DL, L, DIELS, sub_w, sub_t1, sub_l, type=True, pos=True))
DIELS = {"er0": ER0, "td0": TD0, "er1": ER0, "td1": TD0}
CONDS = []
CONDS.append(COND3D(DW, W, H1+T1+H2, T2, DL, L, DIELS, sub_w, sub_t2, sub_l, type=True, pos=True))
conf0 = GET_CONFIGURATION_3D()


DIELS = {"er0": ER2, "td0": TD2, "er1": ER0, "td1": TD0}
CONDS = []
CONDS.append(COND3D(DW, W, H1, T1, DL, L, DIELS, sub_w, sub_t1, sub_l, type=True, pos=True))
DIEL3D(H1, DIELS, CONDS, sub_s, sub_w, sub_l, sub_d)
DIELS = {"er0": ER0, "td0": TD0, "er1": ER2, "td1": TD2}
CONDS = []
CONDS.append(COND3D(DW, W, H1+T1+H2, T2, DL, L, DIELS, sub_w, sub_t2, sub_l, type=True, pos=True))
DIEL3D(H1+T1+H2, DIELS, CONDS, sub_s, sub_w, sub_l, sub_d)
conf = GET_CONFIGURATION_3D()

result = CalMat(conf, conf0, f0, L, loss=loss)
ECHO()
ECHO(json.dumps(result))