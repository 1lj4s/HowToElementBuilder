D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
CC2 = []
CC1.append(cond(2*W1, H1, W1, T, D1, D2, True, False))
diel1(CC1, H1, D1, D2)
CC2.append(cond(2*W1, H1+H2, W1, T, D2, D0, True, False))
diel1(CC2, H1+H2, D2, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
ECHO()
ECHO(json.dumps(result))