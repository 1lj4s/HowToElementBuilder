import math
import numpy as np

def calculate_linear_parameters(er, h, w, t):

    if w / h < 1:
        e_eff = ((er + 1) / 2) + ((er - 1) / 2) * (1 / math.sqrt(1 + 12 * h / w) + 0.04 * (1 - w / h) ** 2)
    else:
        e_eff = (er + 1) / 2 + (er - 1) / 2 * (1 / math.sqrt(1 + 12 * h / w))
    p = t / math.pi * np.log(4 * math.exp(1) / ((t / h) ** 2 + ((1 / math.pi) / ((w / t) + 1.1) )** 2))
    g = p * ((1 + (1 / e_eff)) / 2)
    x = w + g
    a=120 * math.pi / (2 * math.pi * math.sqrt(2) * (math.sqrt(er + 1)))
    c=((4 * h) / x)
    d=(14 + (8 / e_eff)) / 11 * ((4 * h) / x)
    u=((14 + (8 / e_eff)) / 11) ** 2
    m=((4 * h) / x) ** 2
    n=((1 + (1 / e_eff)) / 2) * (math.pi ** 2 )
    b=math.log(1+c * (d +math.sqrt(u * m + n)))
    # Расчет Z0 (волнового сопротивления)
    Z0 = a*b
    L = Z0 / v * np.sqrt(e_eff)  # Гн/м
    C = 1 / (v * Z0 / np.sqrt(e_eff))  # Ф/м
    print('L:',L)
    print('C:', C)
    r=0.0172 #1.68*10**-8
    m0=4*math.pi*10**-7
    f=1*10**9
    # e0=8.85*10**-12
    # om = 2 * math.pi * f
    # mr=0.99
    D=math.sqrt((r/(math.pi*f*m0)))
    # D1=v*math.sqrt(2*(e0/(om*mr)))
    Rs=math.sqrt(math.pi*f*m0*r)
    R=Rs/w*(1+2/math.pi*math.atan(1.4*((D/h)**2)))
    print('R:',R)
    om=2*math.pi*f
    tan=0.017
    G=om*C*tan
    print('G:',G)
    # Потери (если заданы параметры)
    # losse_c, losse_d = None, None
    # if f and tand and rho:
    #     Rs = math.sqrt(math.pi * f * 1e9 * rho * 4e-7 * math.pi)
    #     alpha_c = (Rs / (Z0 * w * 1e-3)) * 8.686
    #     lambda0 = 3e8 / (f * 1e9)
    #     alpha_d = (math.pi * er * (e_eff - 1) * tand) / (lambda0 * math.sqrt(e_eff) * (er - 1)) * 8.686


        # (120 * math.pi / (2 * math.pi * math.sqrt(2)) * math.sqrt(er + 1)) * np.log10(1 + 4 * h / x * ( (14 + (8 / e_eff)) / 11 * (4 * h) / x + math.sqrt(((14 + (8 / e_eff)) / 11) ** 2 * ((4 * h) / x) ** 2 +((1 + (1 / e_eff)) / 2) * (math.pi) ** 2 ) )))
    # if w / h < 1:
    #     Z0 = 60 * math.log(8 * h / w + w / (4 * h), 10)
    # else:
    #     Z0 = (120 * math.pi /2*math.sqrt(2*math.pi)*math.sqrt(er+1))math.log10(1+4*h/x*((14+(8/e_eff))/11*(4*h)/x)+math.sqrt(((14+(8/e_eff)/11)**2)*((4*h)/x)**2+((1+(1/e_eff)/2))*(math.pi)**2))
    #

    # Возвращаем оба параметра
    return e_eff, Z0


# Пример использования:
er = 12.9  # Относительная диэлектрическая проницаемость
h = 0.1  # Высота подложки (мм)
w = 0.07 # Ширина линии (мм)
t = 0.002  # Толщина проводника (мм)
v= 3e8  # Скорость света (м/с)

e_eff, Z0 = calculate_linear_parameters(er, h, w, t)





print(f"Эффективная диэлектрическая проницаемость: {e_eff}")
print(f"Волновое сопротивление: {Z0} Ом")
# print(f"Погонная емкость : {C}")
# print(f"Погонная индуктивность: {L} Ом")





print(np.atan(1))





