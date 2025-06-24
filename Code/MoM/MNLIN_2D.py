D0 = [ER0, MU0, TD0]
D1 = [ER1, MU1, TD1]

SET_INFINITE_GROUND(1)
SET_AUTO_SEGMENT_LENGTH_DIELECTRIC(T / seg_diel)
SET_AUTO_SEGMENT_LENGTH_CONDUCTOR(T / seg_cond)

CC1 = []
D = 2 * W[0]

for i in range(len(S)):
    CC1.append(cond(D, H, W[i], T, D1, D0, True, False))
    D = D + S[i] + W[i]
    print(S[i])
CC1.append(cond(D, H, W[-1], T, D1, D0, True, False))
diel1(CC1, H, D1, D0)

conf = GET_CONFIGURATION_2D()
result = CalMat(conf, f0, loss=loss, sigma=sigma)
ECHO()
ECHO(json.dumps(result))