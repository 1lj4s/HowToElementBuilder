D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
CC1.append(cond(2 * W1, H, W1, T, D1, D0, True, False))
CC1.append(cond(2 * W1 + W1 + S, H, W2, T, D1, D0, True, False))
diel1(CC1, H, D1, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
# result.update({"W": W, "T": T, "f0": f0})
ECHO()
ECHO(json.dumps(result))

