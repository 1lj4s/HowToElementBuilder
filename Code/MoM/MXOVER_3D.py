#SIM:
DW = 5*W1
DL = DW
sub_w = W1 / 10
sub_s = W1 / 10
sub_d = DW / 10
sub_t1 = T / 3
sub_t2 = T2 / 3
sub_l = W2 / 10

SET_INFINITE_GROUND3D(1)

DIELS = {"er0": ER0, "td0": TD0, "er1": ER0, "td1": TD0}
CONDS = []
CONDS.append(COND3D(DW, W1, H1, T, DL, W2, DIELS, sub_w, sub_t1, sub_l, type=True, pos=True))
DIELS = {"er0": ER0, "td0": TD0, "er1": ER0, "td1": TD0}
CONDS = []
CONDS.append(COND3D(DW, W1, H1+T+H2, T2, DL, W2, DIELS, sub_w, sub_t2, sub_l, type=True, pos=True))
conf0 = GET_CONFIGURATION_3D()


DIELS = {"er0": ER2, "td0": TD2, "er1": ER1, "td1": TD1}
CONDS = []
CONDS.append(COND3D(DW, W1, H1, T, DL, W2, DIELS, sub_w, sub_t1, sub_l, type=True, pos=True))
DIEL3D(H1, DIELS, CONDS, sub_w, sub_l, sub_d)
DIELS = {"er0": ER0, "td0": TD0, "er1": ER2, "td1": TD2}
CONDS = []
CONDS.append(COND3D(DW, W1, H1+T+H2, T2, DL, W2, DIELS, sub_w, sub_t2, sub_l, type=True, pos=True))
DIEL3D(H1+T+H2, DIELS, CONDS, sub_w, sub_l, sub_d)

conf = GET_CONFIGURATION_3D()

result = CalMat(conf, conf0, f0, W2, loss=loss)
ECHO()
ECHO(json.dumps(result))