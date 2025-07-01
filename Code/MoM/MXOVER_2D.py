DIELS1 = {"er0": ER2, "mu0": MU2, "td0": TD2, "er1": ER1, "mu1": MU1, "td1": TD1}
DIELS2 = {"er0": ER0, "mu0": MU0, "td0": TD0, "er1": ER2, "mu1": MU2, "td1": TD2}
SUBS = {"sub_s": sub_s, "sub_w": sub_w, "sub_t": sub_t, "sub_d": sub_d}

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
CC2 = []
CC1.append(cond(2*W1, H1, W1, T, SUBS, DIELS1, True, False))
diel1(CC1, H1, SUBS, DIELS1)
CC2.append(cond(2*W1, H1+H2, W1, T, SUBS, DIELS2, True, False))
diel1(CC2, H1+H2, SUBS, DIELS2)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
ECHO()
ECHO(json.dumps(result))