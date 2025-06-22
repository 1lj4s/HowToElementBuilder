D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]
D2 = [ER2, MU2, TD2]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T1 / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T1 / seg_cond)

CONDS = []
CONDS.append(cond(5 * W, H1, W, T1, D1, D2, True, False))
diel1(CONDS, H1, D1, D2)
CONDS = []
CONDS.append(cond(5 * W, H1+T1+H2, W, T2, D2, D0, True, False))
diel1(CONDS, H1+T1+H2, D2, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
ECHO()
ECHO(json.dumps(result))

