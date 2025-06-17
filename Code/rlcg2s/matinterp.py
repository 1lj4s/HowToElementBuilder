import numpy as np
from scipy.interpolate import interp1d

def matrix_interp(dict_list, N):

    #Тут может быть какая то более умная проверка, если она нужна
    # if N < 2:
    #     raise ValueError("N должно быть >= 2")
    # if len(dict_list) < 2:
    #     raise ValueError("Список словарей должен содержать как минимум 2 словаря")

    x_orig = np.linspace(0, 1, len(dict_list))
    x_new = np.linspace(0, 1, N)
    result = []

    for t in x_new:
        idx = np.searchsorted(x_orig, t) - 1
        idx = max(0, min(idx, len(dict_list) - 2))

        if x_orig[idx + 1] == x_orig[idx]:
            alpha = 0.0
        else:
            alpha = (t - x_orig[idx]) / (x_orig[idx + 1] - x_orig[idx])
        start = dict_list[idx]
        stop = dict_list[idx + 1]
        interp_dict = {}

        for key in start:
            start_val = np.array(start[key])
            stop_val = np.array(stop[key])
            interp_val = start_val * (1 - alpha) + stop_val * alpha
            interp_dict[key] = interp_val.tolist()
        result.append(interp_dict)

    return result
if __name__ == "__main__":
    N = 10
    input_dicts = [{'mL': [[6.328772201924097e-07]], 'mC': [[1.3827757045794706e-10]], 'mR': [[[540.1017627943623, 530.12032436557, 538.3044105562898, 426.86561646650296, 461.0675622309043]]], 'mG': [[[0.0036515711988209694, 0.00486876159842796, 0.00608595199803495, 0.007303142397641939, 0.008520332797248929]]]}, {'mL': [[5.600849401272159e-07]], 'mC': [[1.6621195299238554e-10]], 'mR': [[[407.8063004934288, 394.576930700666, 404.8916662255988, 334.99171756462545, 361.83240960843654]]], 'mG': [[[0.004417538182364192, 0.005890050909818922, 0.007362563637273653, 0.008835076364728384, 0.010307589092183114]]]}, {'mL': [[4.87292660062022e-07]], 'mC': [[1.9414633552682402e-10]], 'mR': [[[275.51083819249527, 259.03353703576204, 271.4789218949078, 243.11781866274794, 262.5972569859688]]], 'mG': [[[0.005183505165907413, 0.006911340221209886, 0.008639175276512357, 0.010367010331814827, 0.0120948453871173]]]}]
    for i in range(len(input_dicts)):
        print(input_dicts[i])
    print()
    output_dicts = matrix_interp(input_dicts, N)
    for i in range(len(output_dicts)):
        print(output_dicts[i])