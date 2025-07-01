DIELS = {"er0": ER0, "mu0": MU0, "td0": TD0, "er1": ER1, "mu1": MU1, "td1": TD1}
SUBS = {"sub_s": sub_s, "sub_w": sub_w, "sub_t": sub_t, "sub_d": sub_d}

SET_INFINITE_GROUND(1)

CC1 = []
D = 2 * max(W1, W2)
CC1.append(cond(D, H, W1, T, SUBS, DIELS, True, False))
CC1.append(cond(D + W1 + S, H, W2, T, SUBS, DIELS, True, False))
diel1(CC1, H, SUBS, DIELS)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
# result.update({"W": W, "T": T, "f0": f0})
ECHO()
ECHO(json.dumps(result))

